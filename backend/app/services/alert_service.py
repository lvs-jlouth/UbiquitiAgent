"""Alert service."""
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert


class AlertService:
    """Business logic and CRUD for alerts."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_alerts(
        self,
        skip: int = 0,
        limit: int = 100,
        severity: str | None = None,
        acknowledged: bool | None = None,
    ) -> list[Alert]:
        stmt = select(Alert)
        if severity:
            stmt = stmt.where(Alert.severity == severity)
        if acknowledged is not None:
            stmt = stmt.where(Alert.is_acknowledged == acknowledged)
        stmt = stmt.order_by(Alert.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_alerts(
        self, severity: str | None = None, acknowledged: bool | None = None
    ) -> int:
        stmt = select(func.count()).select_from(Alert)
        if severity:
            stmt = stmt.where(Alert.severity == severity)
        if acknowledged is not None:
            stmt = stmt.where(Alert.is_acknowledged == acknowledged)
        result = await self.db.execute(stmt)
        return int(result.scalar_one())

    async def get_alert(self, alert_id: int) -> Alert | None:
        return await self.db.get(Alert, alert_id)

    async def create_alert(self, alert_data: dict) -> Alert:
        alert = Alert(**alert_data)
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def acknowledge(self, alert_id: int, user_id: int) -> Alert | None:
        alert = await self.get_alert(alert_id)
        if alert is None:
            return None
        alert.is_acknowledged = True
        alert.acknowledged_by = user_id
        alert.acknowledged_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def get_recent_alerts(
        self, severity: str | None = None, limit: int = 50
    ) -> list[Alert]:
        stmt = select(Alert)
        if severity:
            stmt = stmt.where(Alert.severity == severity)
        stmt = stmt.order_by(Alert.created_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
