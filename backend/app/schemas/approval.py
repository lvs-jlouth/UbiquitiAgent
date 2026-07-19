"""Approval schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ApprovalBase(BaseModel):
    recommendation_id: int
    notes: str | None = None


class ApprovalCreate(ApprovalBase):
    requested_by_id: int


class ApprovalDecision(BaseModel):
    """Payload for approving or rejecting an approval."""

    notes: str | None = Field(default=None)


class ApprovalUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None
    reviewed_by_id: int | None = None


class ApprovalResponse(ApprovalBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    requested_by_id: int
    reviewed_by_id: int | None = None
    status: str
    reviewed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
