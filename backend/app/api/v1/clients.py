"""Client endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.client import ClientResponse
from app.schemas.common import PaginatedResponse
from app.services.client_service import ClientService

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=PaginatedResponse[ClientResponse], summary="List clients")
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    known_only: bool | None = Query(None),
    vlan_id: int | None = Query(None),
    ssid: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> PaginatedResponse[ClientResponse]:
    """List network clients with optional filters and pagination."""
    service = ClientService(db)
    clients = await service.list_clients(
        skip=skip, limit=limit, known_only=known_only, vlan_id=vlan_id, ssid=ssid
    )
    total = await service.count_clients(known_only=known_only, vlan_id=vlan_id, ssid=ssid)
    return PaginatedResponse[ClientResponse](
        items=[ClientResponse.model_validate(c) for c in clients],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{client_id}", response_model=ClientResponse, summary="Get a client")
async def get_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> ClientResponse:
    """Get a single client by id."""
    service = ClientService(db)
    client = await service.get_client(client_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return ClientResponse.model_validate(client)


@router.patch(
    "/{client_id}/mark-known", response_model=ClientResponse, summary="Mark a client as known"
)
async def mark_known(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> ClientResponse:
    """Mark a client as a known/trusted device."""
    service = ClientService(db)
    client = await service.mark_known(client_id, True)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return ClientResponse.model_validate(client)
