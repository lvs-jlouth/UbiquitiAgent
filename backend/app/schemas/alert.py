"""Alert schemas."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AlertBase(BaseModel):
    alert_type: str = Field(..., max_length=100)
    severity: str
    title: str = Field(..., max_length=255)
    description: str


class AlertCreate(AlertBase):
    raw_data: dict[str, Any] | None = None


class AlertUpdate(BaseModel):
    alert_type: str | None = None
    severity: str | None = None
    title: str | None = None
    description: str | None = None
    is_acknowledged: bool | None = None
    raw_data: dict[str, Any] | None = None


class AlertResponse(AlertBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_acknowledged: bool
    acknowledged_by: int | None = None
    acknowledged_at: datetime | None = None
    raw_data: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime
