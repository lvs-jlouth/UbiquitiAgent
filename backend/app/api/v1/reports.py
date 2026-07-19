"""Report endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.report import (
    ReportGenerateRequest,
    ReportResponse,
    ReportSummary,
)
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=PaginatedResponse[ReportSummary], summary="List reports")
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> PaginatedResponse[ReportSummary]:
    """List previously generated reports."""
    service = ReportService(db)
    reports = await service.list_reports(skip=skip, limit=limit)
    return PaginatedResponse[ReportSummary](
        items=[ReportSummary.model_validate(r) for r in reports],
        total=len(reports),
        skip=skip,
        limit=limit,
    )


@router.get("/{report_id}", response_model=ReportResponse, summary="Get a report")
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> ReportResponse:
    """Get a single report by id."""
    service = ReportService(db)
    report = await service.get_report(report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return ReportResponse.model_validate(report)


@router.post("/generate", response_model=ReportResponse, summary="Generate a report")
async def generate_report(
    payload: ReportGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ReportResponse:
    """Generate a new report of the requested type."""
    service = ReportService(db)
    try:
        report = await service.generate_report(
            report_type=payload.report_type,
            title=payload.title,
            generated_by=current_user.username,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ReportResponse.model_validate(report)
