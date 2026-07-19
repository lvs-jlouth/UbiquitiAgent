"""Recommendation model."""
from sqlalchemy import JSON, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)  # critical, high, medium, low
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, approved, rejected, applied
    facts: Mapped[list | None] = mapped_column(JSON, nullable=True)
    observations: Mapped[list | None] = mapped_column(JSON, nullable=True)
    risks: Mapped[list | None] = mapped_column(JSON, nullable=True)
    proposed_change: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    audit_finding_id: Mapped[int | None] = mapped_column(
        ForeignKey("audit_findings.id"), nullable=True
    )
