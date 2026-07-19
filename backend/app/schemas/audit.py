"""Audit schemas."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuditFindingBase(BaseModel):
    rule_id: str = Field(..., max_length=100)
    rule_name: str = Field(..., max_length=255)
    severity: str  # critical, high, medium, low, info
    category: str  # security, vlan, wifi, firewall, dns, routing
    title: str = Field(..., max_length=255)
    description: str
    affected_resource: str | None = None
    evidence: dict[str, Any] | None = None
    recommendation: str | None = None


class AuditFindingCreate(AuditFindingBase):
    pass


class AuditFindingUpdate(BaseModel):
    severity: str | None = None
    title: str | None = None
    description: str | None = None
    affected_resource: str | None = None
    evidence: dict[str, Any] | None = None
    recommendation: str | None = None
    is_resolved: bool | None = None


class AuditFindingResponse(AuditFindingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_resolved: bool
    resolved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class AuditRunResponse(BaseModel):
    """Response after triggering an audit run."""

    findings_count: int
    findings: list[AuditFindingResponse]
    ran_at: datetime
