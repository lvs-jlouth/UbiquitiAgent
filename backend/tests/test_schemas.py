"""Tests for Pydantic schema validation and serialization."""
import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.common import PaginatedResponse
from app.schemas.device import DeviceCreate, DeviceResponse
from app.schemas.recommendation import RecommendationCreate
from app.schemas.report import ReportGenerateRequest
from app.schemas.user import UserCreate


def test_user_create_requires_valid_email():
    with pytest.raises(ValidationError):
        UserCreate(username="bob", email="not-an-email", password="password123")


def test_user_create_password_min_length():
    with pytest.raises(ValidationError):
        UserCreate(username="bob", email="bob@example.com", password="short")


def test_device_create_serialization():
    device = DeviceCreate(mac="aa:bb:cc:dd:ee:ff", name="Switch 1", device_type="switch")
    data = device.model_dump()
    assert data["mac"] == "aa:bb:cc:dd:ee:ff"
    assert data["device_type"] == "switch"


def test_login_request_valid():
    req = LoginRequest(username="admin", password="password123")
    assert req.username == "admin"


def test_token_response_defaults():
    token = TokenResponse(access_token="abc", expires_in=1800)
    assert token.token_type == "bearer"


def test_paginated_response_generic():
    page = PaginatedResponse[int](items=[1, 2, 3], total=3, skip=0, limit=10)
    assert page.total == 3
    assert page.items == [1, 2, 3]


def test_recommendation_create_defaults():
    rec = RecommendationCreate(
        title="Segment IoT", description="Add VLAN", category="vlan", priority="high"
    )
    assert rec.ai_generated is False
    assert rec.audit_finding_id is None


def test_report_generate_request_default_type():
    req = ReportGenerateRequest()
    assert req.report_type == "network_health"


def test_device_response_from_attributes():
    class Obj:
        id = 1
        mac = "aa:bb"
        name = "AP"
        device_type = "ap"
        model = "U6"
        firmware_version = "6.0"
        ip_address = "10.0.0.1"
        status = "online"
        site_id = None
        last_seen = None
        raw_data = None
        from datetime import datetime, timezone

        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)

    resp = DeviceResponse.model_validate(Obj())
    assert resp.name == "AP"
    assert resp.id == 1
