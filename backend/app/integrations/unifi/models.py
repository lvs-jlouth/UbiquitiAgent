"""Pydantic models describing normalized UniFi API responses."""
from typing import Any

from pydantic import BaseModel, Field


class UniFiDevice(BaseModel):
    """Normalized UniFi device."""

    mac: str
    name: str = ""
    device_type: str = "other"
    model: str = ""
    firmware_version: str | None = None
    ip_address: str | None = None
    status: str = "unknown"
    site_id: str | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)


class UniFiClient(BaseModel):
    """Normalized UniFi client (station)."""

    mac: str
    hostname: str | None = None
    ip_address: str | None = None
    vlan_id: int | None = None
    ssid: str | None = None
    signal_strength: int | None = None
    device_type: str | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)


class UniFiEvent(BaseModel):
    """Normalized UniFi event."""

    event_type: str
    severity: str = "info"
    source: str = "unifi"
    message: str = ""
    device_mac: str | None = None
    client_mac: str | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)


def normalize_device(raw: dict[str, Any]) -> UniFiDevice:
    """Convert a raw UniFi device payload into a normalized model."""
    type_map = {"ugw": "gateway", "usw": "switch", "uap": "ap"}
    raw_type = str(raw.get("type", "")).lower()
    device_type = type_map.get(raw_type, "other")
    state = raw.get("state")
    status = "online" if state == 1 else ("offline" if state == 0 else "unknown")
    return UniFiDevice(
        mac=raw.get("mac", ""),
        name=raw.get("name") or raw.get("model", "") or raw.get("mac", ""),
        device_type=device_type,
        model=raw.get("model", ""),
        firmware_version=raw.get("version"),
        ip_address=raw.get("ip"),
        status=status,
        site_id=raw.get("site_id"),
        raw_data=raw,
    )


def normalize_client(raw: dict[str, Any]) -> UniFiClient:
    """Convert a raw UniFi client payload into a normalized model."""
    return UniFiClient(
        mac=raw.get("mac", ""),
        hostname=raw.get("hostname") or raw.get("name"),
        ip_address=raw.get("ip"),
        vlan_id=raw.get("vlan") or raw.get("network_id_vlan"),
        ssid=raw.get("essid") or raw.get("ssid"),
        signal_strength=raw.get("signal") or raw.get("rssi"),
        device_type=raw.get("dev_cat") or raw.get("oui"),
        raw_data=raw,
    )


def normalize_event(raw: dict[str, Any]) -> UniFiEvent:
    """Convert a raw UniFi event payload into a normalized model."""
    key = str(raw.get("key", "EVT_Unknown"))
    severity = "info"
    lowered = key.lower()
    if "critical" in lowered or "detect" in lowered:
        severity = "critical"
    elif "error" in lowered or "lost" in lowered or "disconnect" in lowered:
        severity = "error"
    elif "warn" in lowered:
        severity = "warning"
    return UniFiEvent(
        event_type=key,
        severity=severity,
        source="unifi",
        message=raw.get("msg", key),
        device_mac=raw.get("ap") or raw.get("sw") or raw.get("gw"),
        client_mac=raw.get("user") or raw.get("client"),
        raw_data=raw,
    )
