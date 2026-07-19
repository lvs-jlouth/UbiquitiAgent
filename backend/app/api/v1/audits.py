"""Audit endpoints."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.audit import AuditFindingResponse, AuditRunResponse
from app.schemas.common import PaginatedResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audits", tags=["audits"])


@router.get(
    "", response_model=PaginatedResponse[AuditFindingResponse], summary="List audit findings"
)
async def list_findings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    severity: str | None = Query(None),
    category: str | None = Query(None),
    resolved: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> PaginatedResponse[AuditFindingResponse]:
    """List audit findings with optional filters and pagination."""
    service = AuditService(db)
    findings = await service.list_findings(
        skip=skip, limit=limit, severity=severity, category=category, resolved=resolved
    )
    total = await service.count_findings(
        severity=severity, category=category, resolved=resolved
    )
    return PaginatedResponse[AuditFindingResponse](
        items=[AuditFindingResponse.model_validate(f) for f in findings],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{finding_id}", response_model=AuditFindingResponse, summary="Get a finding")
async def get_finding(
    finding_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> AuditFindingResponse:
    """Get a single audit finding by id."""
    service = AuditService(db)
    finding = await service.get_finding(finding_id)
    if finding is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found")
    return AuditFindingResponse.model_validate(finding)


@router.post("/run", response_model=AuditRunResponse, summary="Run a deterministic audit")
async def run_audit(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> AuditRunResponse:
    """Trigger a deterministic configuration audit run."""
    service = AuditService(db)
    findings = await service.run_audit()
    return AuditRunResponse(
        findings_count=len(findings),
        findings=[AuditFindingResponse.model_validate(f) for f in findings],
        ran_at=datetime.now(timezone.utc),
    )


@router.patch(
    "/{finding_id}/resolve", response_model=AuditFindingResponse, summary="Resolve a finding"
)
async def resolve_finding(
    finding_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> AuditFindingResponse:
    """Mark an audit finding as resolved."""
    service = AuditService(db)
    finding = await service.resolve_finding(finding_id)
    if finding is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Finding not found")
    return AuditFindingResponse.model_validate(finding)
