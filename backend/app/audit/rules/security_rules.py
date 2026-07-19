"""Security-focused audit rules."""
from app.audit.rules.base import AuditContext, BaseRule, RuleFinding

# VLAN ids commonly reserved for guest and management networks.
GUEST_KEYWORDS = ("guest", "iot", "visitor")
MGMT_KEYWORDS = ("mgmt", "management", "admin")


class GuestIsolationRule(BaseRule):
    """Verify that guest networks are configured with client isolation."""

    rule_id = "SEC-001"
    rule_name = "Guest Network Isolation"
    severity = "high"
    category = "security"

    async def evaluate(self, context: AuditContext) -> list[RuleFinding]:
        findings: list[RuleFinding] = []
        for network in context.networks:
            name = str(network.get("name", "")).lower()
            purpose = str(network.get("purpose", "")).lower()
            is_guest = purpose == "guest" or any(k in name for k in GUEST_KEYWORDS)
            if not is_guest:
                continue
            isolated = network.get("isolation") or network.get("guest_isolation")
            if not isolated:
                findings.append(
                    self._finding(
                        title=f"Guest network '{network.get('name', 'unknown')}' lacks isolation",
                        description=(
                            "Guest/IoT network does not have client isolation enabled, "
                            "allowing lateral movement between guest devices."
                        ),
                        affected_resource=network.get("name"),
                        evidence={"network": network},
                        recommendation="Enable guest/client isolation on this network.",
                    )
                )
        return findings


class ManagementVLANExposureRule(BaseRule):
    """Detect management networks that are exposed to general clients."""

    rule_id = "SEC-002"
    rule_name = "Management VLAN Exposure"
    severity = "critical"
    category = "security"

    async def evaluate(self, context: AuditContext) -> list[RuleFinding]:
        findings: list[RuleFinding] = []
        mgmt_vlans: set[int] = set()
        for network in context.networks:
            name = str(network.get("name", "")).lower()
            purpose = str(network.get("purpose", "")).lower()
            if purpose == "corporate" and "mgmt" not in name:
                continue
            if any(k in name for k in MGMT_KEYWORDS):
                vlan = network.get("vlan") or network.get("vlan_id")
                if vlan is not None:
                    mgmt_vlans.add(int(vlan))

        for client in context.clients:
            vlan = client.get("vlan_id")
            if vlan is not None and int(vlan) in mgmt_vlans and not client.get("is_known", False):
                findings.append(
                    self._finding(
                        title="Unknown client present on management VLAN",
                        description=(
                            "An unrecognized client is connected to a management VLAN, "
                            "which should be restricted to trusted administrative devices."
                        ),
                        affected_resource=client.get("mac"),
                        evidence={"client": client, "management_vlans": sorted(mgmt_vlans)},
                        recommendation=(
                            "Remove the client from the management VLAN and restrict access "
                            "with firewall rules."
                        ),
                    )
                )
        return findings


class OpenPortForwardRule(BaseRule):
    """Detect port forwards exposing internal services to the internet."""

    rule_id = "SEC-003"
    rule_name = "Open Port Forward"
    severity = "high"
    category = "security"

    RISKY_PORTS = {22, 23, 3389, 445, 3306, 5432, 6379, 27017}

    async def evaluate(self, context: AuditContext) -> list[RuleFinding]:
        findings: list[RuleFinding] = []
        for pf in context.port_forwards:
            if not pf.get("enabled", True):
                continue
            src = str(pf.get("src", "any")).lower()
            dst_port = pf.get("dst_port") or pf.get("fwd_port")
            try:
                dst_port_int = int(dst_port) if dst_port is not None else None
            except (TypeError, ValueError):
                dst_port_int = None
            open_to_any = src in ("any", "0.0.0.0/0", "*", "")
            if open_to_any and (dst_port_int in self.RISKY_PORTS):
                findings.append(
                    self._finding(
                        title=f"Risky port forward exposing port {dst_port_int}",
                        description=(
                            "A port forward exposes a sensitive management/database service "
                            "to any source address on the internet."
                        ),
                        affected_resource=pf.get("name") or str(dst_port_int),
                        evidence={"port_forward": pf},
                        recommendation=(
                            "Restrict the source to trusted IPs or disable the port forward and "
                            "use a VPN instead."
                        ),
                        severity="critical",
                    )
                )
            elif open_to_any:
                findings.append(
                    self._finding(
                        title=f"Port forward open to any source (port {dst_port_int})",
                        description="A port forward accepts traffic from any source address.",
                        affected_resource=pf.get("name") or str(dst_port_int),
                        evidence={"port_forward": pf},
                        recommendation="Limit the allowed source addresses where possible.",
                    )
                )
        return findings


class FirmwareDriftRule(BaseRule):
    """Detect devices running outdated firmware relative to the fleet."""

    rule_id = "SEC-004"
    rule_name = "Firmware Drift"
    severity = "medium"
    category = "security"

    async def evaluate(self, context: AuditContext) -> list[RuleFinding]:
        findings: list[RuleFinding] = []
        # Determine the most common (assumed latest) firmware per model.
        latest_by_model: dict[str, str] = {}
        for device in context.devices:
            model = str(device.get("model", "unknown"))
            fw = device.get("firmware_version")
            if not fw:
                continue
            current = latest_by_model.get(model)
            if current is None or str(fw) > str(current):
                latest_by_model[model] = str(fw)

        for device in context.devices:
            model = str(device.get("model", "unknown"))
            fw = device.get("firmware_version")
            latest = latest_by_model.get(model)
            if fw and latest and str(fw) != latest:
                findings.append(
                    self._finding(
                        title=f"Device '{device.get('name')}' has outdated firmware",
                        description=(
                            f"Device firmware {fw} differs from the newest observed firmware "
                            f"{latest} for model {model}."
                        ),
                        affected_resource=device.get("mac"),
                        evidence={
                            "device": device.get("name"),
                            "current": fw,
                            "latest": latest,
                        },
                        recommendation="Schedule a firmware upgrade to the latest version.",
                    )
                )
            elif not fw:
                findings.append(
                    self._finding(
                        title=f"Device '{device.get('name')}' firmware unknown",
                        description="Firmware version could not be determined for this device.",
                        affected_resource=device.get("mac"),
                        evidence={"device": device.get("name")},
                        recommendation="Verify device connectivity and firmware reporting.",
                        severity="low",
                    )
                )
        return findings
