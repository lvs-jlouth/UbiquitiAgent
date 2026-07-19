"""UniFi integration package."""
from app.integrations.unifi.client import UniFiClient, UniFiError
from app.integrations.unifi.collector import CollectionResult, TelemetryCollector
from app.integrations.unifi.models import (
    UniFiClient as UniFiClientModel,
)
from app.integrations.unifi.models import (
    UniFiDevice,
    UniFiEvent,
    normalize_client,
    normalize_device,
    normalize_event,
)

__all__ = [
    "UniFiClient",
    "UniFiError",
    "CollectionResult",
    "TelemetryCollector",
    "UniFiClientModel",
    "UniFiDevice",
    "UniFiEvent",
    "normalize_client",
    "normalize_device",
    "normalize_event",
]
