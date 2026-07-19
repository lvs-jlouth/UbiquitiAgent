"""Device service."""
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device


class DeviceService:
    """Business logic and CRUD for devices."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_devices(
        self,
        skip: int = 0,
        limit: int = 100,
        device_type: str | None = None,
        status: str | None = None,
    ) -> list[Device]:
        stmt = select(Device)
        if device_type:
            stmt = stmt.where(Device.device_type == device_type)
        if status:
            stmt = stmt.where(Device.status == status)
        stmt = stmt.order_by(Device.name).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_devices(
        self, device_type: str | None = None, status: str | None = None
    ) -> int:
        stmt = select(func.count()).select_from(Device)
        if device_type:
            stmt = stmt.where(Device.device_type == device_type)
        if status:
            stmt = stmt.where(Device.status == status)
        result = await self.db.execute(stmt)
        return int(result.scalar_one())

    async def get_device(self, device_id: int) -> Device | None:
        return await self.db.get(Device, device_id)

    async def get_by_mac(self, mac: str) -> Device | None:
        result = await self.db.execute(select(Device).where(Device.mac == mac))
        return result.scalar_one_or_none()

    async def upsert_device(self, device_data: dict) -> Device:
        """Insert or update a device keyed on MAC address."""
        mac = device_data.get("mac")
        if not mac:
            raise ValueError("device_data must include a 'mac'")
        existing = await self.get_by_mac(mac)
        payload = dict(device_data)
        payload.setdefault("last_seen", datetime.now(timezone.utc))
        if existing is None:
            device = Device(**payload)
            self.db.add(device)
        else:
            for key, value in payload.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            device = existing
        await self.db.commit()
        await self.db.refresh(device)
        return device

    async def get_by_type(self, device_type: str) -> list[Device]:
        result = await self.db.execute(
            select(Device).where(Device.device_type == device_type)
        )
        return list(result.scalars().all())

    async def delete_device(self, device_id: int) -> bool:
        device = await self.get_device(device_id)
        if device is None:
            return False
        await self.db.delete(device)
        await self.db.commit()
        return True
