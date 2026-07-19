"""Health check endpoints."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health", summary="Basic health check")
async def health() -> dict:
    """Return basic service liveness information."""
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/detailed", summary="Detailed health check")
async def health_detailed(request: Request, db: AsyncSession = Depends(get_db)) -> dict:
    """Return detailed health including DB, UniFi, and scheduler status."""
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001
        db_status = "error"

    scheduler = getattr(request.app.state, "scheduler", None)
    scheduler_status = "stopped"
    if scheduler is not None and getattr(scheduler, "running", False):
        scheduler_status = "running"

    unifi_status = "configured" if settings.UNIFI_HOST else "not_configured"

    overall = "ok" if db_status == "ok" else "degraded"
    return {
        "status": overall,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "database": db_status,
            "unifi": unifi_status,
            "scheduler": scheduler_status,
            "operating_mode": settings.OPERATING_MODE,
            "ai_configured": bool(settings.OPENAI_API_KEY),
        },
    }
