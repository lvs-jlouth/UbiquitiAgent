"""Approval endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.approval import ApprovalDecision, ApprovalResponse
from app.schemas.common import PaginatedResponse
from app.services.approval_service import ApprovalService

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("", response_model=PaginatedResponse[ApprovalResponse], summary="List approvals")
async def list_approvals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> PaginatedResponse[ApprovalResponse]:
    """List approvals with optional status filter and pagination."""
    service = ApprovalService(db)
    approvals = await service.list_approvals(skip=skip, limit=limit, status=status_filter)
    total = await service.count_approvals(status=status_filter)
    return PaginatedResponse[ApprovalResponse](
        items=[ApprovalResponse.model_validate(a) for a in approvals],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{approval_id}", response_model=ApprovalResponse, summary="Get an approval")
async def get_approval(
    approval_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> ApprovalResponse:
    """Get a single approval by id."""
    service = ApprovalService(db)
    approval = await service.get_approval(approval_id)
    if approval is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")
    return ApprovalResponse.model_validate(approval)


@router.post(
    "/{approval_id}/approve", response_model=ApprovalResponse, summary="Approve a request"
)
async def approve(
    approval_id: int,
    decision: ApprovalDecision | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
) -> ApprovalResponse:
    """Approve a pending approval request (admin/operator only)."""
    service = ApprovalService(db)
    notes = decision.notes if decision else None
    approval = await service.decide(
        approval_id, approved=True, reviewer_id=current_user.id, notes=notes
    )
    if approval is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")
    return ApprovalResponse.model_validate(approval)


@router.post(
    "/{approval_id}/reject", response_model=ApprovalResponse, summary="Reject a request"
)
async def reject(
    approval_id: int,
    decision: ApprovalDecision | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "operator")),
) -> ApprovalResponse:
    """Reject a pending approval request (admin/operator only)."""
    service = ApprovalService(db)
    notes = decision.notes if decision else None
    approval = await service.decide(
        approval_id, approved=False, reviewer_id=current_user.id, notes=notes
    )
    if approval is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")
    return ApprovalResponse.model_validate(approval)
