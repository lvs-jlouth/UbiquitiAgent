"""Firewall-focused audit rules."""
from app.audit.rules.base import AuditContext, BaseRule, RuleFinding


class ExcessivePermissionsRule(BaseRule):
    """Detect overly permissive allow-any firewall rules."""

    rule_id = "FW-001"
    rule_name = "Excessive Firewall Permissions"
    severity = "high"
    category = "firewall"

    ANY_VALUES = {"any", "0.0.0.0/0", "*", "", "all"}

    async def evaluate(self, context: AuditContext) -> list[RuleFinding]:
        findings: list[RuleFinding] = []
        for rule in context.firewall_rules:
            if not rule.get("enabled", True):
                continue
            action = str(rule.get("action", "")).lower()
            src = str(rule.get("src", rule.get("source", "any"))).lower()
            dst = str(rule.get("dst", rule.get("destination", "any"))).lower()
            if action == "accept" and src in self.ANY_VALUES and dst in self.ANY_VALUES:
                findings.append(
                    self._finding(
                        title=f"Firewall rule '{rule.get('name', 'unnamed')}' allows any-to-any",
                        description=(
                            "A firewall rule permits traffic from any source to any "
                            "destination, effectively bypassing segmentation."
                        ),
                        affected_resource=rule.get("name"),
                        evidence={"rule": rule},
                        recommendation="Restrict the source and destination scope of this rule.",
                    )
                )
        return findings


class HighRiskFirewallRuleRule(BaseRule):
    """Detect firewall rules that allow sensitive ports from untrusted zones."""

    rule_id = "FW-002"
    rule_name = "High Risk Firewall Rule"
    severity = "critical"
    category = "firewall"

    SENSITIVE_PORTS = {22, 23, 3389, 445, 139, 1433, 3306, 5432, 6379, 27017}
    UNTRUSTED_ZONES = {"wan", "guest", "internet", "external"}

    async def evaluate(self, context: AuditContext) -> list[RuleFinding]:
        findings: list[RuleFinding] = []
        for rule in context.firewall_rules:
            if not rule.get("enabled", True):
                continue
            action = str(rule.get("action", "")).lower()
            if action != "accept":
                continue
            src_zone = str(rule.get("src_zone", rule.get("zone", ""))).lower()
            ports = rule.get("dst_ports") or rule.get("ports") or []
            if isinstance(ports, (int, str)):
                ports = [ports]
            port_ints: set[int] = set()
            for p in ports:
                try:
                    port_ints.add(int(p))
                except (TypeError, ValueError):
                    continue
            risky_ports = port_ints & self.SENSITIVE_PORTS
            if src_zone in self.UNTRUSTED_ZONES and risky_ports:
                findings.append(
                    self._finding(
                        title=(
                            f"Firewall rule '{rule.get('name', 'unnamed')}' allows sensitive "
                            f"ports from {src_zone}"
                        ),
                        description=(
                            "A firewall rule permits sensitive service ports "
                            f"({sorted(risky_ports)}) from an untrusted zone."
                        ),
                        affected_resource=rule.get("name"),
                        evidence={"rule": rule, "risky_ports": sorted(risky_ports)},
                        recommendation=(
                            "Block or tightly scope access to these ports from untrusted zones."
                        ),
                    )
                )
        return findings
