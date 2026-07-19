"""APScheduler setup for periodic telemetry collection."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import async_session_factory
from app.integrations.unifi.collector import TelemetryCollector

logger = get_logger(__name__)


async def collect_telemetry() -> None:
    """Scheduled job: collect telemetry from UniFi into the database."""
    if not settings.UNIFI_HOST:
        logger.debug("telemetry_skip", reason="UNIFI_HOST not configured")
        return
    async with async_session_factory() as session:
        collector = TelemetryCollector(session, collected_by="scheduler")
        try:
            await collector.collect_all()
        except Exception as exc:  # noqa: BLE001 - scheduler jobs must not crash the loop
            logger.error("telemetry_job_failed", error=str(exc))


def create_scheduler() -> AsyncIOScheduler:
    """Create and configure the APScheduler instance (not yet started)."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        collect_telemetry,
        trigger="interval",
        seconds=settings.TELEMETRY_INTERVAL_SECONDS,
        id="collect_telemetry",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    return scheduler
