"""Tests for AI tool functions using real services against a test DB."""
import pytest

from app.ai.tools import TOOL_SCHEMAS, execute_tool
from app.ai.tools.audit_tools import run_configuration_audit
from app.ai.tools.network_tools import (
    get_clients,
    get_devices,
    get_network_health,
)
from app.ai.tools.report_tools import ChangeProposal, propose_change
from app.ai.tools.security_tools import get_security_events
from app.services import build_services
from app.services.client_service import ClientService
from app.services.device_service import DeviceService
from app.services.event_service import EventService


@pytest.mark.asyncio
async def test_get_network_health(db_session):
    device_service = DeviceService(db_session)
    await device_service.upsert_device(
        {"mac": "a", "name": "GW", "device_type": "gateway", "status": "online"}
    )
    await device_service.upsert_device(
        {"mac": "b", "name": "SW", "device_type": "switch", "status": "offline"}
    )
    services = build_services(db_session)
    result = await get_network_health(services)
    assert result.total_devices == 2
    assert result.online_devices == 1
    assert 0 <= result.health_score <= 100


@pytest.mark.asyncio
async def test_get_devices_filter(db_session):
    device_service = DeviceService(db_session)
    await device_service.upsert_device(
        {"mac": "a", "name": "AP1", "device_type": "ap"}
    )
    services = build_services(db_session)
    aps = await get_devices(services, device_type="ap")
    assert len(aps) == 1
    assert aps[0].device_type == "ap"


@pytest.mark.asyncio
async def test_get_clients(db_session):
    client_service = ClientService(db_session)
    await client_service.upsert_client({"mac": "c", "hostname": "phone", "vlan_id": 10})
    services = build_services(db_session)
    clients = await get_clients(services, vlan_id=10)
    assert len(clients) == 1
    assert clients[0].vlan_id == 10


@pytest.mark.asyncio
async def test_get_security_events(db_session):
    event_service = EventService(db_session)
    await event_service.create_event(
        {
            "event_type": "EVT_Threat",
            "severity": "critical",
            "source": "unifi",
            "message": "bad",
        }
    )
    services = build_services(db_session)
    events = await get_security_events(services, limit=10)
    assert len(events) == 1


@pytest.mark.asyncio
async def test_run_configuration_audit_tool(db_session):
    from app.models.snapshot import Snapshot

    db_session.add(
        Snapshot(
            snapshot_type="config",
            data={"wlans": [{"name": "Open", "security": "open", "enabled": True}]},
            collected_by="test",
        )
    )
    await db_session.commit()
    services = build_services(db_session)
    result = await run_configuration_audit(services)
    assert result.total_findings >= 1
    assert "critical" in result.by_severity or "high" in result.by_severity


@pytest.mark.asyncio
async def test_propose_change_creates_recommendation(db_session):
    services = build_services(db_session)
    change = ChangeProposal(
        title="Block RDP from WAN",
        description="Add deny rule",
        category="firewall",
        priority="high",
        risks=["temporary disruption"],
    )
    result = await propose_change(services, change)
    assert result.recommendation_id is not None
    assert result.status == "pending"
    rec = await services["recommendation"].get_recommendation(result.recommendation_id)
    assert rec.ai_generated is True


@pytest.mark.asyncio
async def test_execute_tool_dispatch(db_session):
    services = build_services(db_session)
    result = await execute_tool("get_network_health", {}, services)
    assert result.total_devices == 0


@pytest.mark.asyncio
async def test_execute_tool_unknown(db_session):
    services = build_services(db_session)
    with pytest.raises(KeyError):
        await execute_tool("does_not_exist", {}, services)


def test_tool_schemas_wellformed():
    names = {t["function"]["name"] for t in TOOL_SCHEMAS}
    assert "get_network_health" in names
    assert "propose_change" in names
    for schema in TOOL_SCHEMAS:
        assert schema["type"] == "function"
        assert "parameters" in schema["function"]
