"""Aggregate API v1 router."""
from fastapi import APIRouter

from app.api.v1 import (
    agent,
    approvals,
    audits,
    auth,
    clients,
    devices,
    events,
    health,
    recommendations,
    reports,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(devices.router)
api_router.include_router(clients.router)
api_router.include_router(events.router)
api_router.include_router(audits.router)
api_router.include_router(recommendations.router)
api_router.include_router(approvals.router)
api_router.include_router(reports.router)
api_router.include_router(agent.router)

__all__ = ["api_router"]
