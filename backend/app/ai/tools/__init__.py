"""AI tool registry mapping tool names to callables and OpenAI schemas."""
from app.ai.tools import audit_tools, network_tools, report_tools, security_tools
from app.ai.tools.report_tools import ChangeProposal

# Registry: name -> (callable, json schema of parameters)
TOOL_FUNCTIONS = {
    "get_network_health": network_tools.get_network_health,
    "get_devices": network_tools.get_devices,
    "get_clients": network_tools.get_clients,
    "get_access_points": network_tools.get_access_points,
    "get_switches": network_tools.get_switches,
    "get_topology": network_tools.get_topology,
    "get_security_events": security_tools.get_security_events,
    "get_recent_alerts": security_tools.get_recent_alerts,
    "get_firewall_configuration": security_tools.get_firewall_configuration,
    "run_configuration_audit": audit_tools.run_configuration_audit,
    "get_vlan_configuration": audit_tools.get_vlan_configuration,
    "get_dns_configuration": audit_tools.get_dns_configuration,
    "generate_report": report_tools.generate_report,
    "propose_change": report_tools.propose_change,
}


def _tool(name: str, description: str, properties: dict, required: list[str] | None = None) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required or [],
                "additionalProperties": False,
            },
        },
    }


TOOL_SCHEMAS = [
    _tool("get_network_health", "Get overall network health status", {}),
    _tool(
        "get_devices",
        "Get all network devices, optionally filtered by type (gateway, switch, ap, other)",
        {"device_type": {"type": "string", "description": "Filter by device type"}},
    ),
    _tool(
        "get_clients",
        "Get network clients, optionally filtered by VLAN or known status",
        {
            "vlan_id": {"type": "integer", "description": "Filter by VLAN id"},
            "known_only": {"type": "boolean", "description": "Only known clients"},
        },
    ),
    _tool("get_access_points", "Get wireless access points", {}),
    _tool("get_switches", "Get switches", {}),
    _tool("get_topology", "Get network topology", {}),
    _tool(
        "get_security_events",
        "Get recent security events",
        {"limit": {"type": "integer", "description": "Max events to return"}},
    ),
    _tool(
        "get_recent_alerts",
        "Get recent alerts, optionally filtered by severity",
        {"severity": {"type": "string", "description": "Filter by severity"}},
    ),
    _tool("get_firewall_configuration", "Get firewall rules and port forwards", {}),
    _tool("run_configuration_audit", "Run the deterministic configuration audit", {}),
    _tool("get_vlan_configuration", "Get VLAN configuration", {}),
    _tool("get_dns_configuration", "Get DNS configuration", {}),
    _tool(
        "generate_report",
        "Generate a report of a given type (network_health, security, audit, inventory)",
        {"report_type": {"type": "string", "description": "Report type"}},
        required=["report_type"],
    ),
    _tool(
        "propose_change",
        "Propose a network change (creates a pending recommendation requiring approval)",
        {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "category": {"type": "string"},
            "priority": {"type": "string"},
            "proposed_change": {"type": "object", "additionalProperties": True},
            "risks": {"type": "array", "items": {"type": "string"}},
        },
        required=["title", "description"],
    ),
]


async def execute_tool(name: str, arguments: dict, services: dict):
    """Execute a registered tool by name with the given arguments."""
    func = TOOL_FUNCTIONS.get(name)
    if func is None:
        raise KeyError(f"Unknown tool: {name}")
    args = dict(arguments or {})
    if name == "propose_change":
        change = ChangeProposal(**args)
        return await func(services, change=change)
    return await func(services, **args)


__all__ = ["TOOL_FUNCTIONS", "TOOL_SCHEMAS", "execute_tool", "ChangeProposal"]
