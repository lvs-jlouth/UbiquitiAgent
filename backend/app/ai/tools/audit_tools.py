"""AI tools for running audits and inspecting configuration via services."""
from pydantic import BaseModel, Field


class AuditFindingSummary(BaseModel):
    rule_id: str
    rule_name: str
    severity: str
    category: str
    title: str
    affected_resource: str | None = None
    recommendation: str | None = None


class AuditResult(BaseModel):
    total_findings: int
    by_severity: dict[str, int] = Field(default_factory=dict)
    findings: list[AuditFindingSummary] = Field(default_factory=list)


class VLANConfig(BaseModel):
    networks: list[dict] = Field(default_factory=list)
    vlan_ids: list[int] = Field(default_factory=list)


class DNSConfig(BaseModel):
    settings: dict = Field(default_factory=dict)


async def run_configuration_audit(services: dict) -> AuditResult:
    """Run the deterministic configuration audit and return findings."""
    audit_service = services["audit"]
    findings = await audit_service.run_audit()
    by_severity: dict[str, int] = {}
    summaries: list[AuditFindingSummary] = []
    for f in findings:
        by_severity[f.severity] = by_severity.get(f.severity, 0) + 1
        summaries.append(
            AuditFindingSummary(
                rule_id=f.rule_id,
                rule_name=f.rule_name,
                severity=f.severity,
                category=f.category,
                title=f.title,
                affected_resource=f.affected_resource,
                recommendation=f.recommendation,
            )
        )
    return AuditResult(
        total_findings=len(findings),
        by_severity=by_severity,
        findings=summaries,
    )


async def get_vlan_configuration(services: dict) -> VLANConfig:
    """Get VLAN configuration from the most recent snapshot."""
    context = await services["audit"].build_context()
    vlan_ids: list[int] = []
    for n in context.networks:
        vlan = n.get("vlan") or n.get("vlan_id")
        if vlan is not None:
            try:
                vlan_ids.append(int(vlan))
            except (TypeError, ValueError):
                continue
    return VLANConfig(networks=context.networks, vlan_ids=sorted(set(vlan_ids)))


async def get_dns_configuration(services: dict) -> DNSConfig:
    """Get DNS configuration from the most recent snapshot."""
    context = await services["audit"].build_context()
    return DNSConfig(settings=context.dns)
