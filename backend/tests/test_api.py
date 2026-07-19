"""Integration tests for API endpoints via the ASGI app."""
import pytest


@pytest.mark.asyncio
async def test_login_success_and_me(client, test_user):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token

    me = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bear"+"er " + token}
    )
    assert me.status_code == 200
    assert me.json()["username"] == "admin"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client, test_user):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_requires_auth(client):
    resp = await client.get("/api/v1/devices")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_devices_list_with_auth(client, auth_headers):
    resp = await client.get("/api/v1/devices", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 0


@pytest.mark.asyncio
async def test_run_audit_endpoint(client, auth_headers):
    resp = await client.post("/api/v1/audits/run", headers=auth_headers)
    assert resp.status_code == 200
    assert "findings_count" in resp.json()


@pytest.mark.asyncio
async def test_generate_report_endpoint(client, auth_headers):
    resp = await client.post(
        "/api/v1/reports/generate",
        json={"report_type": "inventory"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["report_type"] == "inventory"
    assert body["id"] is not None


@pytest.mark.asyncio
async def test_generate_report_invalid_type(client, auth_headers):
    resp = await client.post(
        "/api/v1/reports/generate",
        json={"report_type": "bogus"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_agent_chat_without_key_returns_503(client, auth_headers):
    resp = await client.post(
        "/api/v1/agent/chat",
        json={"message": "hello"},
        headers=auth_headers,
    )
    # No OpenAI key configured in the test environment.
    assert resp.status_code == 503
