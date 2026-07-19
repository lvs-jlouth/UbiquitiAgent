"""Recommendation schemas."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RecommendationBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str
    category: str = Field(..., max_length=100)
    priority: str  # critical, high, medium, low
    facts: list[Any] | None = None
    observations: list[Any] | None = None
    risks: list[Any] | None = None
    proposed_change: dict[str, Any] | None = None


class RecommendationCreate(RecommendationBase):
    ai_generated: bool = False
    audit_finding_id: int | None = None


class RecommendationUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    priority: str | None = None
    status: str | None = None
    facts: list[Any] | None = None
    observations: list[Any] | None = None
    risks: list[Any] | None = None
    proposed_change: dict[str, Any] | None = None


class RecommendationResponse(RecommendationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    ai_generated: bool
    audit_finding_id: int | None = None
    created_at: datetime
    updated_at: datetime
