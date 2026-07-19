"""Snapshot model."""
from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Snapshot(Base):
    __tablename__ = "snapshots"

    snapshot_type: Mapped[str] = mapped_column(String(100), nullable=False)  # topology, config, telemetry
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
    collected_by: Mapped[str] = mapped_column(String(100), nullable=False)  # scheduler, manual, api
