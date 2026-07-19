"""Device schemas."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DeviceBase(BaseModel):
    mac: str = Field(..., max_length=17)
    name: str = Field(..., max_length=255)
    device_type: str = "other"
    model: str = ""
    firmware_version: str | None = None
    ip_address: str | None = None
    status: str = "unknown"
    site_id: str | None = None


class DeviceCreate(DeviceBase):
    raw_data: dict[str, Any] | None = None


class DeviceUpdate(BaseModel):
    name: str | None = None
    device_type: str | None = None
    model: str | None = None
    firmware_version: str | None = None
    ip_address: str | None = None
    status: str | None = None
    site_id: str | None = None
    raw_data: dict[str, Any] | None = None


class DeviceResponse(DeviceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_seen: datetime | None = None
    raw_data: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime
