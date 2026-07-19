"""Tests for health endpoints."""
import pytest


@pytest.mark.asyncio
async def test_health_ok(client):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["version"]
    assert "timestamp" in body


@pytest.mark.asyncio
async def test_health_detailed(client):
    resp = await client.get("/api/v1/health/detailed")
    assert resp.status_code == 200
    body = resp.json()
    assert "components" in body
    assert body["components"]["database"] == "ok"
    assert "operating_mode" in body["components"]


@pytest.mark.asyncio
async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.json()["api"] == "/api/v1"
