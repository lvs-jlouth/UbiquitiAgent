"""Tests for deterministic audit rules and the audit engine."""
import pytest

from app.audit.engine import AuditEngine
from app.audit.rules.base import AuditContext
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


@pytest.mark.asyncio
async def test_guest_isolation_rule_flags_missing_isolation():
    ctx = AuditContext(
        networks=[{"name": "Guest WiFi", "purpose": "guest", "isolation": False}]
    )
    findings = await GuestIsolationRule().evaluate(ctx)
    assert len(findings) == 1
    assert findings[0].rule_id == "SEC-001"


@pytest.mark.asyncio
async def test_guest_isolation_rule_passes_with_isolation():
    ctx = AuditContext(
        networks=[{"name": "Guest WiFi", "purpose": "guest", "isolation": True}]
    )
    findings = await GuestIsolationRule().evaluate(ctx)
    assert findings == []


@pytest.mark.asyncio
async def test_management_vlan_exposure_rule():
    ctx = AuditContext(
        networks=[{"name": "Management", "vlan": 99}],
        clients=[{"mac": "aa:bb", "vlan_id": 99, "is_known": False}],
    )
    findings = await ManagementVLANExposureRule().evaluate(ctx)
    assert len(findings) == 1
    assert findings[0].severity == "critical"


@pytest.mark.asyncio
async def test_open_port_forward_rule_critical_port():
    ctx = AuditContext(
        port_forwards=[{"name": "ssh", "src": "any", "dst_port": 22, "enabled": True}]
    )
    findings = await OpenPortForwardRule().evaluate(ctx)
    assert len(findings) == 1
    assert findings[0].severity == "critical"


@pytest.mark.asyncio
async def test_firmware_drift_rule():
    ctx = AuditContext(
        devices=[
            {"mac": "a", "name": "AP1", "model": "U6", "firmware_version": "6.0.0"},
            {"mac": "b", "name": "AP2", "model": "U6", "firmware_version": "6.1.0"},
        ]
    )
    findings = await FirmwareDriftRule().evaluate(ctx)
    assert any("outdated" in f.title for f in findings)


@pytest.mark.asyncio
async def test_missing_vlan_segmentation_rule():
    clients = [{"mac": f"m{i}", "vlan_id": 1} for i in range(12)]
    ctx = AuditContext(networks=[{"name": "Default", "vlan": 1}], clients=clients)
    findings = await MissingVLANSegmentationRule().evaluate(ctx)
    assert len(findings) == 1


@pytest.mark.asyncio
async def test_vlan_consistency_rule():
    ctx = AuditContext(
        networks=[{"name": "Default", "vlan": 1}],
        clients=[{"mac": "x", "vlan_id": 50}],
    )
    findings = await VLANConsistencyRule().evaluate(ctx)
    assert len(findings) == 1
    assert "undefined VLAN" in findings[0].title


@pytest.mark.asyncio
async def test_weak_wifi_security_rule():
    ctx = AuditContext(
        wlans=[{"name": "OpenNet", "security": "open", "enabled": True}]
    )
    findings = await WeakWiFiSecurityRule().evaluate(ctx)
    assert len(findings) == 1
    assert findings[0].severity == "critical"


@pytest.mark.asyncio
async def test_high_channel_utilization_rule():
    ctx = AuditContext(
        devices=[
            {
                "mac": "a",
                "name": "AP1",
                "device_type": "ap",
                "raw_data": {"channel_utilization": 90},
            }
        ]
    )
    findings = await HighChannelUtilizationRule().evaluate(ctx)
    assert len(findings) == 1


@pytest.mark.asyncio
async def test_excessive_permissions_rule():
    ctx = AuditContext(
        firewall_rules=[
            {"name": "AllowAll", "action": "accept", "src": "any", "dst": "any"}
        ]
    )
    findings = await ExcessivePermissionsRule().evaluate(ctx)
    assert len(findings) == 1


@pytest.mark.asyncio
async def test_high_risk_firewall_rule():
    ctx = AuditContext(
        firewall_rules=[
            {
                "name": "WAN-RDP",
                "action": "accept",
                "src_zone": "wan",
                "dst_ports": [3389],
            }
        ]
    )
    findings = await HighRiskFirewallRuleRule().evaluate(ctx)
    assert len(findings) == 1
    assert findings[0].severity == "critical"


@pytest.mark.asyncio
async def test_audit_engine_runs_all_rules():
    engine = AuditEngine()
    assert len(engine.rules) == 10
    ctx = AuditContext(
        networks=[{"name": "Guest", "purpose": "guest", "isolation": False}],
        wlans=[{"name": "Open", "security": "open", "enabled": True}],
    )
    findings = await engine.run_audit(ctx)
    rule_ids = {f.rule_id for f in findings}
    assert "SEC-001" in rule_ids
    assert "WIFI-001" in rule_ids


@pytest.mark.asyncio
async def test_audit_engine_empty_context_no_crash():
    engine = AuditEngine()
    findings = await engine.run_audit(AuditContext())
    assert isinstance(findings, list)
