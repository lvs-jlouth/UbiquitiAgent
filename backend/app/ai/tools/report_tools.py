"""AI tools for report generation and change proposals via services."""
from pydantic import BaseModel, Field

from app.core.config import settings


class ReportResult(BaseModel):
    id: int
    report_type: str
    title: str
    summary: str
    sections: list[dict] = Field(default_factory=list)


class ChangeProposal(BaseModel):
    """Structured proposal for a network change (never auto-applied)."""

    title: str
    description: str
    category: str = "general"
    priority: str = "medium"
    proposed_change: dict = Field(default_factory=dict)
    risks: list[str] = Field(default_factory=list)


class ChangeProposalResult(BaseModel):
    recommendation_id: int
    status: str
    requires_approval: bool
    message: str


async def generate_report(services: dict, report_type: str) -> ReportResult:
    """Generate a specific type of report."""
    report = await services["report"].generate_report(
        report_type=report_type, generated_by="ai_agent"
    )
    return ReportResult(
        id=report["id"],
        report_type=report["report_type"],
        title=report["title"],
        summary=report["summary"],
        sections=report["sections"],
    )


async def propose_change(services: dict, change: ChangeProposal) -> ChangeProposalResult:
    """Propose a network change. Always creates a pending recommendation.

    The AI can never apply changes directly; proposals require human approval
    unless the platform is explicitly in ``authorized_change`` mode.
    """
    rec = await services["recommendation"].create_recommendation(
        {
            "title": change.title,
            "description": change.description,
            "category": change.category,
            "priority": change.priority,
            "status": "pending",
            "proposed_change": change.proposed_change,
            "risks": change.risks,
            "ai_generated": True,
        }
    )
    requires_approval = settings.OPERATING_MODE != "authorized_change"
    message = (
        "Change proposal recorded and awaiting human approval."
        if requires_approval
        else "Change proposal recorded; platform is in authorized_change mode."
    )
    return ChangeProposalResult(
        recommendation_id=rec.id,
        status=rec.status,
        requires_approval=requires_approval,
        message=message,
    )
