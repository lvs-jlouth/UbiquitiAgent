"""Approval service."""
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval import Approval
from app.models.recommendation import Recommendation


class ApprovalService:
    """Business logic and CRUD for approvals."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_approvals(
        self, skip: int = 0, limit: int = 100, status: str | None = None
    ) -> list[Approval]:
        stmt = select(Approval)
        if status:
            stmt = stmt.where(Approval.status == status)
        stmt = stmt.order_by(Approval.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_approvals(self, status: str | None = None) -> int:
        stmt = select(func.count()).select_from(Approval)
        if status:
            stmt = stmt.where(Approval.status == status)
        result = await self.db.execute(stmt)
        return int(result.scalar_one())

    async def get_approval(self, approval_id: int) -> Approval | None:
        return await self.db.get(Approval, approval_id)

    async def request_approval(
        self, recommendation_id: int, requested_by_id: int, notes: str | None = None
    ) -> Approval:
        approval = Approval(
            recommendation_id=recommendation_id,
            requested_by_id=requested_by_id,
            notes=notes,
            status="pending",
        )
        self.db.add(approval)
        # Reflect the request on the recommendation itself if present.
        rec = await self.db.get(Recommendation, recommendation_id)
        if rec is not None and rec.status == "pending":
            rec.status = "pending"
        await self.db.commit()
        await self.db.refresh(approval)
        return approval

    async def decide(
        self,
        approval_id: int,
        approved: bool,
        reviewer_id: int,
        notes: str | None = None,
    ) -> Approval | None:
        approval = await self.get_approval(approval_id)
        if approval is None:
            return None
        approval.status = "approved" if approved else "rejected"
        approval.reviewed_by_id = reviewer_id
        approval.reviewed_at = datetime.now(timezone.utc)
        if notes is not None:
            approval.notes = notes
        rec = await self.db.get(Recommendation, approval.recommendation_id)
        if rec is not None:
            rec.status = "approved" if approved else "rejected"
        await self.db.commit()
        await self.db.refresh(approval)
        return approval
