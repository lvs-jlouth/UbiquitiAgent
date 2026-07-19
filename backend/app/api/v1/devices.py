"""Device endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.integrations.unifi.collector import TelemetryCollector
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.device import DeviceResponse
from app.services.device_service import DeviceService

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("", response_model=PaginatedResponse[DeviceResponse], summary="List devices")
async def list_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    device_type: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> PaginatedResponse[DeviceResponse]:
    """List network devices with optional filters and pagination."""
    service = DeviceService(db)
    devices = await service.list_devices(
        skip=skip, limit=limit, device_type=device_type, status=status_filter
    )
    total = await service.count_devices(device_type=device_type, status=status_filter)
    return PaginatedResponse[DeviceResponse](
        items=[DeviceResponse.model_validate(d) for d in devices],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{device_id}", response_model=DeviceResponse, summary="Get a device")
async def get_device(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> DeviceResponse:
    """Get a single device by id."""
    service = DeviceService(db)
    device = await service.get_device(device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return DeviceResponse.model_validate(device)


@router.post("/refresh", summary="Trigger a manual device refresh from UniFi")
async def refresh_devices(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> dict:
    """Trigger a manual telemetry collection from UniFi."""
    if not settings.UNIFI_HOST:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="UniFi integration is not configured",
        )
    collector = TelemetryCollector(db, collected_by="manual")
    result = await collector.collect_all()
    return result.model_dump()
