"""Event service."""
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event


class EventService:
    """Business logic and CRUD for events."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_events(
        self,
        skip: int = 0,
        limit: int = 100,
        severity: str | None = None,
        event_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[Event]:
        stmt = select(Event)
        if severity:
            stmt = stmt.where(Event.severity == severity)
        if event_type:
            stmt = stmt.where(Event.event_type == event_type)
        if start_date:
            stmt = stmt.where(Event.created_at >= start_date)
        if end_date:
            stmt = stmt.where(Event.created_at <= end_date)
        stmt = stmt.order_by(Event.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_events(
        self,
        severity: str | None = None,
        event_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(Event)
        if severity:
            stmt = stmt.where(Event.severity == severity)
        if event_type:
            stmt = stmt.where(Event.event_type == event_type)
        if start_date:
            stmt = stmt.where(Event.created_at >= start_date)
        if end_date:
            stmt = stmt.where(Event.created_at <= end_date)
        result = await self.db.execute(stmt)
        return int(result.scalar_one())

    async def get_event(self, event_id: int) -> Event | None:
        return await self.db.get(Event, event_id)

    async def create_event(self, event_data: dict) -> Event:
        event = Event(**event_data)
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def get_security_events(self, limit: int = 50) -> list[Event]:
        stmt = (
            select(Event)
            .where(Event.severity.in_(["warning", "error", "critical"]))
            .order_by(Event.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
