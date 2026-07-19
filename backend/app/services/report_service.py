"""Report service - generates and stores operational reports.

Reports are persisted as ``Snapshot`` rows with ``snapshot_type='report'`` so no
additional table is required.
"""
from datetime import datetime, timezone

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.snapshot import Snapshot
from app.services.audit_service import AuditService
from app.services.client_service import ClientService
from app.services.device_service import DeviceService
from app.services.event_service import EventService

REPORT_TYPES = {"network_health", "security", "audit", "inventory"}


class ReportService:
    """Generates deterministic operational reports and persists them."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_report(
        self, report_type: str, title: str | None = None, generated_by: str = "api"
    ) -> dict:
        if report_type not in REPORT_TYPES:
            raise ValueError(f"Unknown report_type '{report_type}'")

        if report_type == "network_health":
            payload = await self._network_health()
        elif report_type == "security":
            payload = await self._security()
        elif report_type == "audit":
            payload = await self._audit()
        else:
            payload = await self._inventory()

        report = {
            "report_type": report_type,
            "title": title or payload["title"],
            "summary": payload["summary"],
            "sections": payload["sections"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": generated_by,
        }

        snapshot = Snapshot(
            snapshot_type="report",
            data=report,
            collected_by=generated_by,
        )
        self.db.add(snapshot)
        await self.db.commit()
        await self.db.refresh(snapshot)

        report_with_id = dict(report)
        report_with_id["id"] = snapshot.id
        report_with_id["generated_at"] = snapshot.created_at
        return report_with_id

    async def list_reports(self, skip: int = 0, limit: int = 100) -> list[dict]:
        stmt = (
            select(Snapshot)
            .where(Snapshot.snapshot_type == "report")
            .order_by(desc(Snapshot.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        reports: list[dict] = []
        for snapshot in result.scalars().all():
            data = snapshot.data or {}
            reports.append(
                {
                    "id": snapshot.id,
                    "report_type": data.get("report_type", "unknown"),
                    "title": data.get("title", "Report"),
                    "generated_at": snapshot.created_at,
                }
            )
        return reports

    async def get_report(self, report_id: int) -> dict | None:
        stmt = select(Snapshot).where(
            and_(Snapshot.id == report_id, Snapshot.snapshot_type == "report")
        )
        result = await self.db.execute(stmt)
        snapshot = result.scalar_one_or_none()
        if snapshot is None:
            return None
        data = dict(snapshot.data or {})
        data["id"] = snapshot.id
        data["generated_at"] = snapshot.created_at
        return data

    # ------------------------------------------------------------------
    # Report builders
    # ------------------------------------------------------------------
    async def _network_health(self) -> dict:
        device_service = DeviceService(self.db)
        client_service = ClientService(self.db)
        total_devices = await device_service.count_devices()
        online = await device_service.count_devices(status="online")
        offline = await device_service.count_devices(status="offline")
        total_clients = await client_service.count_clients()
        known = await client_service.count_clients(known_only=True)
        summary = (
            f"{online}/{total_devices} devices online, {total_clients} clients "
            f"({known} known)."
        )
        return {
            "title": "Network Health Report",
            "summary": summary,
            "sections": [
                {
                    "heading": "Devices",
                    "content": f"Total {total_devices}, online {online}, offline {offline}.",
                    "data": {
                        "total": total_devices,
                        "online": online,
                        "offline": offline,
                    },
                },
                {
                    "heading": "Clients",
                    "content": f"Total {total_clients}, known {known}.",
                    "data": {"total": total_clients, "known": known},
                },
            ],
        }

    async def _security(self) -> dict:
        event_service = EventService(self.db)
        audit_service = AuditService(self.db)
        security_events = await event_service.get_security_events(limit=100)
        critical = await audit_service.count_findings(severity="critical", resolved=False)
        high = await audit_service.count_findings(severity="high", resolved=False)
        summary = (
            f"{len(security_events)} recent security events; "
            f"{critical} critical and {high} high open findings."
        )
        return {
            "title": "Security Report",
            "summary": summary,
            "sections": [
                {
                    "heading": "Open Findings",
                    "content": f"Critical: {critical}, High: {high}.",
                    "data": {"critical": critical, "high": high},
                },
                {
                    "heading": "Recent Security Events",
                    "content": f"{len(security_events)} events in the recent window.",
                    "data": {"count": len(security_events)},
                },
            ],
        }

    async def _audit(self) -> dict:
        audit_service = AuditService(self.db)
        total = await audit_service.count_findings(resolved=False)
        by_category = {}
        for category in ("security", "vlan", "wifi", "firewall", "dns", "routing"):
            by_category[category] = await audit_service.count_findings(
                category=category, resolved=False
            )
        summary = f"{total} unresolved audit findings across categories."
        return {
            "title": "Configuration Audit Report",
            "summary": summary,
            "sections": [
                {
                    "heading": "Findings by Category",
                    "content": ", ".join(f"{k}: {v}" for k, v in by_category.items()),
                    "data": by_category,
                }
            ],
        }

    async def _inventory(self) -> dict:
        device_service = DeviceService(self.db)
        devices = await device_service.list_devices(limit=1000)
        by_type: dict[str, int] = {}
        for device in devices:
            by_type[device.device_type] = by_type.get(device.device_type, 0) + 1
        summary = f"Inventory of {len(devices)} devices."
        return {
            "title": "Inventory Report",
            "summary": summary,
            "sections": [
                {
                    "heading": "Devices by Type",
                    "content": ", ".join(f"{k}: {v}" for k, v in by_type.items()) or "None",
                    "data": by_type,
                }
            ],
        }
