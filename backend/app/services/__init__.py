"""Service layer package."""
from app.services.alert_service import AlertService
from app.services.approval_service import ApprovalService
from app.services.audit_service import AuditService
from app.services.client_service import ClientService
from app.services.device_service import DeviceService
from app.services.event_service import EventService
from app.services.recommendation_service import RecommendationService
from app.services.report_service import ReportService
from app.services.user_service import UserService

__all__ = [
    "AlertService",
    "ApprovalService",
    "AuditService",
    "ClientService",
    "DeviceService",
    "EventService",
    "RecommendationService",
    "ReportService",
    "UserService",
    "build_services",
]


def build_services(db) -> dict:
    """Construct a dictionary of service instances bound to a DB session.

    Used by the AI agent and API layer to inject all available services.
    """
    return {
        "alert": AlertService(db),
        "approval": ApprovalService(db),
        "audit": AuditService(db),
        "client": ClientService(db),
        "device": DeviceService(db),
        "event": EventService(db),
        "recommendation": RecommendationService(db),
        "report": ReportService(db),
        "user": UserService(db),
    }
