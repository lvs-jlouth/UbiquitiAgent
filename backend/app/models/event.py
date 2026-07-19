"""Event model."""
from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Event(Base):
    __tablename__ = "events"

    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="info")  # info, warning, error, critical
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    device_mac: Mapped[str | None] = mapped_column(String(17), nullable=True)
    client_mac: Mapped[str | None] = mapped_column(String(17), nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
