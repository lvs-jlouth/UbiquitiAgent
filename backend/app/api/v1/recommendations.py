"""Recommendation endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.approval import ApprovalResponse
from app.schemas.common import PaginatedResponse
from app.schemas.recommendation import RecommendationResponse
from app.services.approval_service import ApprovalService
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get(
    "",
    response_model=PaginatedResponse[RecommendationResponse],
    summary="List recommendations",
)
async def list_recommendations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: str | None = Query(None, alias="status"),
    category: str | None = Query(None),
    priority: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> PaginatedResponse[RecommendationResponse]:
    """List recommendations with optional filters and pagination."""
    service = RecommendationService(db)
    recs = await service.list_recommendations(
        skip=skip, limit=limit, status=status_filter, category=category, priority=priority
    )
    total = await service.count_recommendations(
        status=status_filter, category=category, priority=priority
    )
    return PaginatedResponse[RecommendationResponse](
        items=[RecommendationResponse.model_validate(r) for r in recs],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{rec_id}", response_model=RecommendationResponse, summary="Get a recommendation"
)
async def get_recommendation(
    rec_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> RecommendationResponse:
    """Get a single recommendation by id."""
    service = RecommendationService(db)
    rec = await service.get_recommendation(rec_id)
    if rec is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found"
        )
    return RecommendationResponse.model_validate(rec)


@router.post(
    "/{rec_id}/request-approval",
    response_model=ApprovalResponse,
    summary="Request approval for a recommendation",
)
async def request_approval(
    rec_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ApprovalResponse:
    """Create an approval request for a recommendation."""
    rec_service = RecommendationService(db)
    rec = await rec_service.get_recommendation(rec_id)
    if rec is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found"
        )
    approval_service = ApprovalService(db)
    approval = await approval_service.request_approval(
        recommendation_id=rec_id, requested_by_id=current_user.id
    )
    return ApprovalResponse.model_validate(approval)
