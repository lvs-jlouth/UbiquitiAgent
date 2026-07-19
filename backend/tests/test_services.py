"""Tests for the service layer CRUD operations."""
import pytest

from app.services.audit_service import AuditService
from app.services.client_service import ClientService
from app.services.device_service import DeviceService
from app.services.event_service import EventService
from app.services.recommendation_service import RecommendationService
from app.services.report_service import ReportService
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_user_service_create_and_authenticate(db_session):
    service = UserService(db_session)
    user = await service.create_user(
        username="alice", email="alice@example.com", password="password123", role="operator"
    )
    assert user.id is not None
    authed = await service.authenticate("alice", "password123")
    assert authed is not None
    assert await service.authenticate("alice", "wrong") is None


@pytest.mark.asyncio
async def test_device_service_upsert(db_session):
    service = DeviceService(db_session)
    d1 = await service.upsert_device({"mac": "aa:bb", "name": "SW1", "device_type": "switch"})
    assert d1.name == "SW1"
    d2 = await service.upsert_device({"mac": "aa:bb", "name": "SW1-renamed"})
    assert d2.id == d1.id
    assert d2.name == "SW1-renamed"
    assert await service.count_devices() == 1
    assert await service.count_devices(device_type="switch") == 1


@pytest.mark.asyncio
async def test_client_service_mark_known(db_session):
    service = ClientService(db_session)
    client = await service.upsert_client({"mac": "cc:dd", "hostname": "laptop"})
    assert client.is_known is False
    updated = await service.mark_known(client.id, True)
    assert updated.is_known is True
    known = await service.list_clients(known_only=True)
    assert len(known) == 1


@pytest.mark.asyncio
async def test_event_service_security_events(db_session):
    service = EventService(db_session)
    await service.create_event(
        {"event_type": "EVT_Info", "severity": "info", "source": "unifi", "message": "ok"}
    )
    await service.create_event(
        {
            "event_type": "EVT_Threat",
            "severity": "critical",
            "source": "unifi",
            "message": "threat",
        }
    )
    security = await service.get_security_events()
    assert len(security) == 1
    assert security[0].severity == "critical"


@pytest.mark.asyncio
async def test_audit_service_run_persists_findings(db_session):
    device_service = DeviceService(db_session)
    await device_service.upsert_device(
        {"mac": "a", "name": "AP1", "device_type": "ap", "model": "U6", "firmware_version": "6.0"}
    )
    from app.models.snapshot import Snapshot

    snapshot = Snapshot(
        snapshot_type="config",
        data={
            "networks": [{"name": "Guest", "purpose": "guest", "isolation": False}],
            "wlans": [{"name": "Open", "security": "open", "enabled": True}],
        },
        collected_by="test",
    )
    db_session.add(snapshot)
    await db_session.commit()

    service = AuditService(db_session)
    findings = await service.run_audit()
    assert len(findings) >= 2
    stored = await service.list_findings()
    assert len(stored) == len(findings)


@pytest.mark.asyncio
async def test_recommendation_service_status_flow(db_session):
    service = RecommendationService(db_session)
    rec = await service.create_recommendation(
        {
            "title": "Segment IoT",
            "description": "Add VLAN",
            "category": "vlan",
            "priority": "high",
        }
    )
    assert rec.status == "pending"
    updated = await service.update_status(rec.id, "approved")
    assert updated.status == "approved"


@pytest.mark.asyncio
async def test_report_service_generate(db_session):
    device_service = DeviceService(db_session)
    await device_service.upsert_device(
        {"mac": "a", "name": "GW", "device_type": "gateway", "status": "online"}
    )
    service = ReportService(db_session)
    report = await service.generate_report("network_health", generated_by="tester")
    assert report["id"] is not None
    assert report["report_type"] == "network_health"
    reports = await service.list_reports()
    assert len(reports) == 1
    fetched = await service.get_report(report["id"])
    assert fetched["title"] == report["title"]
