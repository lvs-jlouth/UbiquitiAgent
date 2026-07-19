"""AI tools for querying network state via services.

Every tool accepts a ``services`` dict (see ``app.services.build_services``) and
returns a Pydantic model. Tools never touch the database or network directly.
"""
from pydantic import BaseModel, Field


class DeviceSummary(BaseModel):
    mac: str
    name: str
    device_type: str
    model: str
    status: str
    firmware_version: str | None = None
    ip_address: str | None = None


class ClientSummary(BaseModel):
    mac: str
    hostname: str | None = None
    ip_address: str | None = None
    vlan_id: int | None = None
    ssid: str | None = None
    is_known: bool = False


class APSummary(BaseModel):
    mac: str
    name: str
    model: str
    status: str
    client_count: int = 0


class SwitchSummary(BaseModel):
    mac: str
    name: str
    model: str
    status: str
    port_count: int = 0


class NetworkHealthResult(BaseModel):
    total_devices: int
    online_devices: int
    offline_devices: int
    total_clients: int
    known_clients: int
    unknown_clients: int
    health_score: float = Field(..., ge=0, le=100)
    status: str


class TopologyResult(BaseModel):
    nodes: list[dict] = Field(default_factory=list)
    edges: list[dict] = Field(default_factory=list)
    vlan_map: dict = Field(default_factory=dict)


def _device_summary(device) -> DeviceSummary:
    return DeviceSummary(
        mac=device.mac,
        name=device.name,
        device_type=device.device_type,
        model=device.model,
        status=device.status,
        firmware_version=device.firmware_version,
        ip_address=device.ip_address,
    )


async def get_network_health(services: dict) -> NetworkHealthResult:
    """Get overall network health status."""
    device_service = services["device"]
    client_service = services["client"]
    total_devices = await device_service.count_devices()
    online = await device_service.count_devices(status="online")
    offline = await device_service.count_devices(status="offline")
    total_clients = await client_service.count_clients()
    known = await client_service.count_clients(known_only=True)
    unknown = total_clients - known

    if total_devices == 0:
        score = 100.0
    else:
        score = round((online / total_devices) * 100, 1)
    status = "healthy" if score >= 90 else ("degraded" if score >= 60 else "unhealthy")
    return NetworkHealthResult(
        total_devices=total_devices,
        online_devices=online,
        offline_devices=offline,
        total_clients=total_clients,
        known_clients=known,
        unknown_clients=unknown,
        health_score=score,
        status=status,
    )


async def get_devices(services: dict, device_type: str | None = None) -> list[DeviceSummary]:
    """Get all network devices, optionally filtered by type."""
    devices = await services["device"].list_devices(limit=1000, device_type=device_type)
    return [_device_summary(d) for d in devices]


async def get_clients(
    services: dict, vlan_id: int | None = None, known_only: bool = False
) -> list[ClientSummary]:
    """Get network clients, optionally filtered by VLAN or known status."""
    clients = await services["client"].list_clients(
        limit=1000, vlan_id=vlan_id, known_only=True if known_only else None
    )
    return [
        ClientSummary(
            mac=c.mac,
            hostname=c.hostname,
            ip_address=c.ip_address,
            vlan_id=c.vlan_id,
            ssid=c.ssid,
            is_known=c.is_known,
        )
        for c in clients
    ]


async def get_access_points(services: dict) -> list[APSummary]:
    """Get wireless access points."""
    devices = await services["device"].get_by_type("ap")
    summaries: list[APSummary] = []
    for d in devices:
        raw = d.raw_data or {}
        summaries.append(
            APSummary(
                mac=d.mac,
                name=d.name,
                model=d.model,
                status=d.status,
                client_count=int(raw.get("num_sta", 0) or 0),
            )
        )
    return summaries


async def get_switches(services: dict) -> list[SwitchSummary]:
    """Get switches."""
    devices = await services["device"].get_by_type("switch")
    summaries: list[SwitchSummary] = []
    for d in devices:
        raw = d.raw_data or {}
        summaries.append(
            SwitchSummary(
                mac=d.mac,
                name=d.name,
                model=d.model,
                status=d.status,
                port_count=int(raw.get("num_port", 0) or 0),
            )
        )
    return summaries


async def get_topology(services: dict) -> TopologyResult:
    """Get network topology derived from devices and clients."""
    device_service = services["device"]
    client_service = services["client"]
    devices = await device_service.list_devices(limit=1000)
    clients = await client_service.list_clients(limit=1000)

    nodes = [
        {"id": d.mac, "label": d.name, "type": d.device_type, "status": d.status}
        for d in devices
    ]
    gateways = [d for d in devices if d.device_type == "gateway"]
    edges = []
    if gateways:
        gw = gateways[0]
        for d in devices:
            if d.mac != gw.mac:
                edges.append({"source": gw.mac, "target": d.mac})

    vlan_map: dict[str, list[str]] = {}
    for c in clients:
        if c.vlan_id is not None:
            vlan_map.setdefault(str(c.vlan_id), []).append(c.mac)

    return TopologyResult(nodes=nodes, edges=edges, vlan_map=vlan_map)
