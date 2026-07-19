"""Audit rules package with default rule registry."""
from app.audit.rules.base import AuditContext, BaseRule, RuleFinding
from app.audit.rules.firewall_rules import (
    ExcessivePermissionsRule,
    HighRiskFirewallRuleRule,
)
from app.audit.rules.security_rules import (
    FirmwareDriftRule,
    GuestIsolationRule,
    ManagementVLANExposureRule,
    OpenPortForwardRule,
)
from app.audit.rules.vlan_rules import (
    MissingVLANSegmentationRule,
    VLANConsistencyRule,
)
from app.audit.rules.wifi_rules import (
    HighChannelUtilizationRule,
    WeakWiFiSecurityRule,
)


def default_rules() -> list[BaseRule]:
    """Return an instance of every built-in audit rule."""
    return [
        GuestIsolationRule(),
        ManagementVLANExposureRule(),
        OpenPortForwardRule(),
        FirmwareDriftRule(),
        MissingVLANSegmentationRule(),
        VLANConsistencyRule(),
        WeakWiFiSecurityRule(),
        HighChannelUtilizationRule(),
        ExcessivePermissionsRule(),
        HighRiskFirewallRuleRule(),
    ]


__all__ = [
    "AuditContext",
    "BaseRule",
    "RuleFinding",
    "ExcessivePermissionsRule",
    "HighRiskFirewallRuleRule",
    "FirmwareDriftRule",
    "GuestIsolationRule",
    "ManagementVLANExposureRule",
    "OpenPortForwardRule",
    "MissingVLANSegmentationRule",
    "VLANConsistencyRule",
    "HighChannelUtilizationRule",
    "WeakWiFiSecurityRule",
    "default_rules",
]
