"""Report schemas."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ReportGenerateRequest(BaseModel):
    """Request to generate a report."""

    report_type: str = Field(
        default="network_health",
        description="One of: network_health, security, audit, inventory",
    )
    title: str | None = None


class ReportSection(BaseModel):
    """A single section within a report."""

    heading: str
    content: str
    data: dict[str, Any] | None = None


class ReportResponse(BaseModel):
    """Generated report response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    report_type: str
    title: str
    summary: str
    sections: list[ReportSection]
    generated_at: datetime
    generated_by: str


class ReportSummary(BaseModel):
    """Lightweight report list item."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    report_type: str
    title: str
    generated_at: datetime
