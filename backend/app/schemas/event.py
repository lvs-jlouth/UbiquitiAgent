"""Event schemas."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventBase(BaseModel):
    event_type: str = Field(..., max_length=100)
    severity: str = "info"
    source: str = Field(..., max_length=100)
    message: str
    device_mac: str | None = None
    client_mac: str | None = None


class EventCreate(EventBase):
    raw_data: dict[str, Any] | None = None


class EventUpdate(BaseModel):
    event_type: str | None = None
    severity: str | None = None
    source: str | None = None
    message: str | None = None
    device_mac: str | None = None
    client_mac: str | None = None
    raw_data: dict[str, Any] | None = None


class EventResponse(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    raw_data: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime
