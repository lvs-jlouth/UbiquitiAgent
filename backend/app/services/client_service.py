"""Client service."""
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client


class ClientService:
    """Business logic and CRUD for network clients."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_clients(
        self,
        skip: int = 0,
        limit: int = 100,
        known_only: bool | None = None,
        vlan_id: int | None = None,
        ssid: str | None = None,
    ) -> list[Client]:
        stmt = select(Client)
        if known_only is not None:
            stmt = stmt.where(Client.is_known == known_only)
        if vlan_id is not None:
            stmt = stmt.where(Client.vlan_id == vlan_id)
        if ssid:
            stmt = stmt.where(Client.ssid == ssid)
        stmt = stmt.order_by(Client.mac).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_clients(
        self,
        known_only: bool | None = None,
        vlan_id: int | None = None,
        ssid: str | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(Client)
        if known_only is not None:
            stmt = stmt.where(Client.is_known == known_only)
        if vlan_id is not None:
            stmt = stmt.where(Client.vlan_id == vlan_id)
        if ssid:
            stmt = stmt.where(Client.ssid == ssid)
        result = await self.db.execute(stmt)
        return int(result.scalar_one())

    async def get_client(self, client_id: int) -> Client | None:
        return await self.db.get(Client, client_id)

    async def get_by_mac(self, mac: str) -> Client | None:
        result = await self.db.execute(select(Client).where(Client.mac == mac))
        return result.scalar_one_or_none()

    async def upsert_client(self, client_data: dict) -> Client:
        mac = client_data.get("mac")
        if not mac:
            raise ValueError("client_data must include a 'mac'")
        existing = await self.get_by_mac(mac)
        payload = dict(client_data)
        payload.setdefault("last_seen", datetime.now(timezone.utc))
        if existing is None:
            client = Client(**payload)
            self.db.add(client)
        else:
            for key, value in payload.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            client = existing
        await self.db.commit()
        await self.db.refresh(client)
        return client

    async def mark_known(self, client_id: int, is_known: bool = True) -> Client | None:
        client = await self.get_client(client_id)
        if client is None:
            return None
        client.is_known = is_known
        await self.db.commit()
        await self.db.refresh(client)
        return client

    async def delete_client(self, client_id: int) -> bool:
        client = await self.get_client(client_id)
        if client is None:
            return False
        await self.db.delete(client)
        await self.db.commit()
        return True
