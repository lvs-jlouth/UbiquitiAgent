"""AI tools for querying security state via services."""
from pydantic import BaseModel, Field


class SecurityEventSummary(BaseModel):
    id: int
    event_type: str
    severity: str
    source: str
    message: str
    device_mac: str | None = None
    client_mac: str | None = None


class AlertSummary(BaseModel):
    id: int
    alert_type: str
    severity: str
    title: str
    description: str
    is_acknowledged: bool


class FirewallRuleSummary(BaseModel):
    name: str | None = None
    action: str | None = None
    enabled: bool = True
    src: str | None = None
    dst: str | None = None


class FirewallConfig(BaseModel):
    rules: list[FirewallRuleSummary] = Field(default_factory=list)
    port_forwards: list[dict] = Field(default_factory=list)
    total_rules: int = 0


async def get_security_events(services: dict, limit: int = 50) -> list[SecurityEventSummary]:
    """Get recent security events (warning severity and above)."""
    events = await services["event"].get_security_events(limit=limit)
    return [
        SecurityEventSummary(
            id=e.id,
            event_type=e.event_type,
            severity=e.severity,
            source=e.source,
            message=e.message,
            device_mac=e.device_mac,
            client_mac=e.client_mac,
        )
        for e in events
    ]


async def get_recent_alerts(services: dict, severity: str | None = None) -> list[AlertSummary]:
    """Get recent alerts, optionally filtered by severity."""
    alerts = await services["alert"].get_recent_alerts(severity=severity, limit=50)
    return [
        AlertSummary(
            id=a.id,
            alert_type=a.alert_type,
            severity=a.severity,
            title=a.title,
            description=a.description,
            is_acknowledged=a.is_acknowledged,
        )
        for a in alerts
    ]


async def get_firewall_configuration(services: dict) -> FirewallConfig:
    """Get firewall rules from the most recent configuration snapshot."""
    audit_service = services["audit"]
    context = await audit_service.build_context()
    rules = [
        FirewallRuleSummary(
            name=r.get("name"),
            action=r.get("action"),
            enabled=r.get("enabled", True),
            src=str(r.get("src", r.get("source", ""))) or None,
            dst=str(r.get("dst", r.get("destination", ""))) or None,
        )
        for r in context.firewall_rules
    ]
    return FirewallConfig(
        rules=rules,
        port_forwards=context.port_forwards,
        total_rules=len(rules),
    )
