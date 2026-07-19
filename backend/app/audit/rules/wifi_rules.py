"""Wireless-focused audit rules."""
from app.audit.rules.base import AuditContext, BaseRule, RuleFinding

WEAK_SECURITY = {"open", "none", "wep", "wpa", "wpa-psk"}


class WeakWiFiSecurityRule(BaseRule):
    """Detect WLANs using weak or no encryption."""

    rule_id = "WIFI-001"
    rule_name = "Weak WiFi Security"
    severity = "high"
    category = "wifi"

    async def evaluate(self, context: AuditContext) -> list[RuleFinding]:
        findings: list[RuleFinding] = []
        for wlan in context.wlans:
            security = str(wlan.get("security", "")).lower()
            enabled = wlan.get("enabled", True)
            if not enabled:
                continue
            if security in WEAK_SECURITY or security == "":
                severity = "critical" if security in ("open", "none", "", "wep") else "high"
                findings.append(
                    self._finding(
                        title=f"WLAN '{wlan.get('name', 'unknown')}' uses weak security",
                        description=(
                            f"The wireless network uses '{security or 'open'}' security. "
                            "Modern WPA2/WPA3 encryption should be used."
                        ),
                        affected_resource=wlan.get("name"),
                        evidence={"wlan": wlan},
                        recommendation="Reconfigure the WLAN to use WPA2 or WPA3 encryption.",
                        severity=severity,
                    )
                )
        return findings


class HighChannelUtilizationRule(BaseRule):
    """Detect access points on congested channels."""

    rule_id = "WIFI-002"
    rule_name = "High Channel Utilization"
    severity = "medium"
    category = "wifi"

    UTILIZATION_THRESHOLD = 75

    async def evaluate(self, context: AuditContext) -> list[RuleFinding]:
        findings: list[RuleFinding] = []
        for device in context.devices:
            if device.get("device_type") != "ap":
                continue
            raw = device.get("raw_data") or {}
            utilization = raw.get("channel_utilization")
            if utilization is None:
                continue
            try:
                util_val = float(utilization)
            except (TypeError, ValueError):
                continue
            if util_val >= self.UTILIZATION_THRESHOLD:
                findings.append(
                    self._finding(
                        title=f"AP '{device.get('name')}' has high channel utilization",
                        description=(
                            f"Channel utilization is {util_val:.0f}%, above the "
                            f"{self.UTILIZATION_THRESHOLD}% threshold, degrading performance."
                        ),
                        affected_resource=device.get("mac"),
                        evidence={"device": device.get("name"), "utilization": util_val},
                        recommendation=(
                            "Change the channel, reduce transmit power, or add capacity."
                        ),
                    )
                )
        return findings
