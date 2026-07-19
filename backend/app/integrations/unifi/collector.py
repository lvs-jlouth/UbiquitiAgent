"""Telemetry collector that pulls data from UniFi and persists it."""
from datetime import datetime, timezone

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.integrations.unifi.client import UniFiClient, UniFiError
from app.integrations.unifi.models import (
    normalize_client,
    normalize_device,
    normalize_event,
)
from app.models.snapshot import Snapshot
from app.services.client_service import ClientService
from app.services.device_service import DeviceService
from app.services.event_service import EventService

logger = get_logger(__name__)


class CollectionResult(BaseModel):
    """Summary of a telemetry collection run."""

    devices: int = 0
    clients: int = 0
    events: int = 0
    errors: list[str] = Field(default_factory=list)
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TelemetryCollector:
    """Collects telemetry from UniFi and stores it in the database."""

    def __init__(
        self,
        db: AsyncSession,
        client: UniFiClient | None = None,
        collected_by: str = "scheduler",
    ):
        self.db = db
        self.collected_by = collected_by
        self.client = client or UniFiClient(
            host=settings.UNIFI_HOST,
            port=settings.UNIFI_PORT,
            username=settings.UNIFI_USERNAME,
            password=settings.UNIFI_PASSWORD,
            site=settings.UNIFI_SITE,
            verify_ssl=settings.UNIFI_VERIFY_SSL,
        )

    async def collect_devices(self) -> list[dict]:
        raw_devices = await self.client.get_devices()
        return [normalize_device(d).model_dump() for d in raw_devices]

    async def collect_clients(self) -> list[dict]:
        raw_clients = await self.client.get_clients()
        return [normalize_client(c).model_dump() for c in raw_clients]

    async def collect_events(self) -> list[dict]:
        raw_events = await self.client.get_events()
        return [normalize_event(e).model_dump() for e in raw_events]

    async def collect_config(self) -> dict:
        """Collect configuration used by the audit engine."""
        return {
            "networks": await self.client.get_network_config(),
            "wlans": await self.client.get_wlan_config(),
            "firewall_rules": await self.client.get_firewall_rules(),
            "port_forwards": await self.client.get_port_forwards(),
            "routing": await self.client.get_routing(),
            "dns": await self.client.get_dns_settings(),
            "site_stats": await self.client.get_site_stats(),
        }

    async def collect_all(self) -> CollectionResult:
        """Collect devices, clients, events, and config from UniFi and persist."""
        result = CollectionResult()
        device_service = DeviceService(self.db)
        client_service = ClientService(self.db)
        event_service = EventService(self.db)

        try:
            await self.client.login()
        except UniFiError as exc:
            result.errors.append(f"login: {exc}")
            logger.warning("unifi_login_failed", error=str(exc))
            return result

        try:
            for device in await self.collect_devices():
                if device.get("mac"):
                    await device_service.upsert_device(device)
                    result.devices += 1
        except UniFiError as exc:
            result.errors.append(f"devices: {exc}")

        try:
            for client in await self.collect_clients():
                if client.get("mac"):
                    await client_service.upsert_client(client)
                    result.clients += 1
        except UniFiError as exc:
            result.errors.append(f"clients: {exc}")

        try:
            for event in await self.collect_events():
                await event_service.create_event(event)
                result.events += 1
        except UniFiError as exc:
            result.errors.append(f"events: {exc}")

        try:
            config = await self.collect_config()
            snapshot = Snapshot(
                snapshot_type="config",
                data=config,
                collected_by=self.collected_by,
            )
            self.db.add(snapshot)
            await self.db.commit()
        except UniFiError as exc:
            result.errors.append(f"config: {exc}")

        await self.client.logout()
        logger.info(
            "telemetry_collected",
            devices=result.devices,
            clients=result.clients,
            events=result.events,
            errors=len(result.errors),
        )
        return result
