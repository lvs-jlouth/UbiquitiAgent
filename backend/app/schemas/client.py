"""Client schemas."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ClientBase(BaseModel):
    mac: str = Field(..., max_length=17)
    hostname: str | None = None
    ip_address: str | None = None
    vlan_id: int | None = None
    ssid: str | None = None
    signal_strength: int | None = None
    is_known: bool = False
    device_type: str | None = None


class ClientCreate(ClientBase):
    raw_data: dict[str, Any] | None = None


class ClientUpdate(BaseModel):
    hostname: str | None = None
    ip_address: str | None = None
    vlan_id: int | None = None
    ssid: str | None = None
    signal_strength: int | None = None
    is_known: bool | None = None
    device_type: str | None = None
    raw_data: dict[str, Any] | None = None


class ClientResponse(ClientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_seen: datetime | None = None
    raw_data: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime
