"""Event endpoints."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.event import EventResponse
from app.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=PaginatedResponse[EventResponse], summary="List events")
async def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    severity: str | None = Query(None),
    event_type: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> PaginatedResponse[EventResponse]:
    """List events with optional filters and pagination."""
    service = EventService(db)
    events = await service.list_events(
        skip=skip,
        limit=limit,
        severity=severity,
        event_type=event_type,
        start_date=start_date,
        end_date=end_date,
    )
    total = await service.count_events(
        severity=severity, event_type=event_type, start_date=start_date, end_date=end_date
    )
    return PaginatedResponse[EventResponse](
        items=[EventResponse.model_validate(e) for e in events],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{event_id}", response_model=EventResponse, summary="Get an event")
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> EventResponse:
    """Get a single event by id."""
    service = EventService(db)
    event = await service.get_event(event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return EventResponse.model_validate(event)
