"""VLAN-focused audit rules."""
from app.audit.rules.base import AuditContext, BaseRule, RuleFinding


class MissingVLANSegmentationRule(BaseRule):
    """Detect flat networks lacking VLAN segmentation."""

    rule_id = "VLAN-001"
    rule_name = "Missing VLAN Segmentation"
    severity = "medium"
    category = "vlan"

    async def evaluate(self, context: AuditContext) -> list[RuleFinding]:
        findings: list[RuleFinding] = []
        vlan_ids = {
            n.get("vlan") or n.get("vlan_id")
            for n in context.networks
            if (n.get("vlan") or n.get("vlan_id")) is not None
        }
        # Consider IoT / guest devices present among clients.
        has_iot = any(
            "iot" in str(c.get("device_type", "")).lower()
            or "iot" in str(c.get("hostname", "")).lower()
            for c in context.clients
        )
        if len(vlan_ids) <= 1 and (has_iot or len(context.clients) > 10):
            findings.append(
                self._finding(
                    title="Network lacks VLAN segmentation",
                    description=(
                        "The network appears to run on a single flat VLAN despite hosting "
                        "many or mixed-trust devices. Segmentation limits blast radius."
                    ),
                    affected_resource="network",
                    evidence={
                        "vlan_count": len(vlan_ids),
                        "client_count": len(context.clients),
                        "has_iot": has_iot,
                    },
                    recommendation=(
                        "Introduce separate VLANs for IoT, guest, and corporate devices."
                    ),
                )
            )
        return findings


class VLANConsistencyRule(BaseRule):
    """Detect clients on VLANs that are not defined in the network config."""

    rule_id = "VLAN-002"
    rule_name = "VLAN Consistency"
    severity = "low"
    category = "vlan"

    async def evaluate(self, context: AuditContext) -> list[RuleFinding]:
        findings: list[RuleFinding] = []
        defined_vlans = {
            int(n.get("vlan") or n.get("vlan_id"))
            for n in context.networks
            if (n.get("vlan") or n.get("vlan_id")) is not None
        }
        if not defined_vlans:
            return findings
        for client in context.clients:
            vlan = client.get("vlan_id")
            if vlan is not None and int(vlan) not in defined_vlans:
                findings.append(
                    self._finding(
                        title=f"Client on undefined VLAN {vlan}",
                        description=(
                            "A client is assigned to a VLAN that is not defined in the "
                            "network configuration, indicating a misconfiguration."
                        ),
                        affected_resource=client.get("mac"),
                        evidence={
                            "client": client.get("mac"),
                            "vlan": vlan,
                            "defined_vlans": sorted(defined_vlans),
                        },
                        recommendation="Define the VLAN or reassign the client to a valid VLAN.",
                    )
                )
        return findings
