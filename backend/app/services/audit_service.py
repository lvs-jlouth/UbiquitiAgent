"""Audit service - builds context, runs the engine, persists findings."""
from datetime import datetime, timezone

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.engine import AuditEngine
from app.audit.rules.base import AuditContext, RuleFinding
from app.models.audit_finding import AuditFinding
from app.models.client import Client
from app.models.device import Device
from app.models.snapshot import Snapshot


class AuditService:
    """Runs deterministic audits and manages audit findings."""

    def __init__(self, db: AsyncSession, engine: AuditEngine | None = None):
        self.db = db
        self.engine = engine or AuditEngine()

    async def build_context(self) -> AuditContext:
        """Assemble an AuditContext from stored devices, clients, and config snapshots."""
        devices = list((await self.db.execute(select(Device))).scalars().all())
        clients = list((await self.db.execute(select(Client))).scalars().all())

        device_dicts = [
            {
                "mac": d.mac,
                "name": d.name,
                "device_type": d.device_type,
                "model": d.model,
                "firmware_version": d.firmware_version,
                "status": d.status,
                "raw_data": d.raw_data or {},
            }
            for d in devices
        ]
        client_dicts = [
            {
                "mac": c.mac,
                "hostname": c.hostname,
                "vlan_id": c.vlan_id,
                "ssid": c.ssid,
                "is_known": c.is_known,
                "device_type": c.device_type,
            }
            for c in clients
        ]

        config = await self._latest_config_snapshot()
        return AuditContext(
            devices=device_dicts,
            clients=client_dicts,
            networks=config.get("networks", []),
            wlans=config.get("wlans", []),
            firewall_rules=config.get("firewall_rules", []),
            port_forwards=config.get("port_forwards", []),
            routing=config.get("routing", []),
            dns=config.get("dns", {}),
            site_stats=config.get("site_stats", {}),
        )

    async def _latest_config_snapshot(self) -> dict:
        stmt = (
            select(Snapshot)
            .where(Snapshot.snapshot_type == "config")
            .order_by(desc(Snapshot.created_at))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        snapshot = result.scalar_one_or_none()
        return snapshot.data if snapshot and snapshot.data else {}

    async def run_audit(self, context: AuditContext | None = None) -> list[AuditFinding]:
        """Run the audit engine and persist the resulting findings."""
        if context is None:
            context = await self.build_context()
        rule_findings = await self.engine.run_audit(context)
        persisted = [await self._persist_finding(f) for f in rule_findings]
        await self.db.commit()
        for finding in persisted:
            await self.db.refresh(finding)
        return persisted

    async def _persist_finding(self, finding: RuleFinding) -> AuditFinding:
        model = AuditFinding(
            rule_id=finding.rule_id,
            rule_name=finding.rule_name,
            severity=finding.severity,
            category=finding.category,
            title=finding.title,
            description=finding.description,
            affected_resource=finding.affected_resource,
            evidence=finding.evidence,
            recommendation=finding.recommendation,
        )
        self.db.add(model)
        return model

    async def list_findings(
        self,
        skip: int = 0,
        limit: int = 100,
        severity: str | None = None,
        category: str | None = None,
        resolved: bool | None = None,
    ) -> list[AuditFinding]:
        stmt = select(AuditFinding)
        if severity:
            stmt = stmt.where(AuditFinding.severity == severity)
        if category:
            stmt = stmt.where(AuditFinding.category == category)
        if resolved is not None:
            stmt = stmt.where(AuditFinding.is_resolved == resolved)
        stmt = stmt.order_by(AuditFinding.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_findings(
        self,
        severity: str | None = None,
        category: str | None = None,
        resolved: bool | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(AuditFinding)
        if severity:
            stmt = stmt.where(AuditFinding.severity == severity)
        if category:
            stmt = stmt.where(AuditFinding.category == category)
        if resolved is not None:
            stmt = stmt.where(AuditFinding.is_resolved == resolved)
        result = await self.db.execute(stmt)
        return int(result.scalar_one())

    async def get_finding(self, finding_id: int) -> AuditFinding | None:
        return await self.db.get(AuditFinding, finding_id)

    async def resolve_finding(self, finding_id: int) -> AuditFinding | None:
        finding = await self.get_finding(finding_id)
        if finding is None:
            return None
        finding.is_resolved = True
        finding.resolved_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(finding)
        return finding
