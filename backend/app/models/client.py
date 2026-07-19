"""Client model."""
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Client(Base):
    __tablename__ = "clients"

    mac: Mapped[str] = mapped_column(String(17), unique=True, nullable=False)
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    vlan_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ssid: Mapped[str | None] = mapped_column(String(100), nullable=True)
    signal_strength: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_known: Mapped[bool] = mapped_column(Boolean, default=False)
    device_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
