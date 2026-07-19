"""Recommendation service."""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recommendation import Recommendation


class RecommendationService:
    """Business logic and CRUD for recommendations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_recommendations(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        category: str | None = None,
        priority: str | None = None,
    ) -> list[Recommendation]:
        stmt = select(Recommendation)
        if status:
            stmt = stmt.where(Recommendation.status == status)
        if category:
            stmt = stmt.where(Recommendation.category == category)
        if priority:
            stmt = stmt.where(Recommendation.priority == priority)
        stmt = stmt.order_by(Recommendation.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_recommendations(
        self,
        status: str | None = None,
        category: str | None = None,
        priority: str | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(Recommendation)
        if status:
            stmt = stmt.where(Recommendation.status == status)
        if category:
            stmt = stmt.where(Recommendation.category == category)
        if priority:
            stmt = stmt.where(Recommendation.priority == priority)
        result = await self.db.execute(stmt)
        return int(result.scalar_one())

    async def get_recommendation(self, rec_id: int) -> Recommendation | None:
        return await self.db.get(Recommendation, rec_id)

    async def create_recommendation(self, data: dict) -> Recommendation:
        rec = Recommendation(**data)
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def update_status(self, rec_id: int, status: str) -> Recommendation | None:
        rec = await self.get_recommendation(rec_id)
        if rec is None:
            return None
        rec.status = status
        await self.db.commit()
        await self.db.refresh(rec)
        return rec
