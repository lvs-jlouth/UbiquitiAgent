"""Topology model."""
from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Topology(Base):
    __tablename__ = "topologies"

    nodes: Mapped[list] = mapped_column(JSON, nullable=False)  # list of device nodes
    edges: Mapped[list] = mapped_column(JSON, nullable=False)  # list of connections
    vlan_map: Mapped[dict] = mapped_column(JSON, nullable=False)
    snapshot_id: Mapped[int | None] = mapped_column(ForeignKey("snapshots.id"), nullable=True)
