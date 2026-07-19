"""FastAPI application entrypoint."""
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger, request_id_ctx, trace_id_ctx
from app.db.session import init_db
from app.integrations.scheduler import create_scheduler

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    logger.info("startup", app=settings.APP_NAME, version=settings.APP_VERSION)
    try:
        await init_db()
    except Exception as exc:  # noqa: BLE001 - allow startup even if DB is unavailable
        logger.error("db_init_failed", error=str(exc))

    scheduler = create_scheduler()
    try:
        scheduler.start()
        app.state.scheduler = scheduler
        logger.info("scheduler_started")
    except Exception as exc:  # noqa: BLE001
        logger.error("scheduler_start_failed", error=str(exc))
        app.state.scheduler = None

    yield

    scheduler = getattr(app.state, "scheduler", None)
    if scheduler is not None:
        try:
            scheduler.shutdown(wait=False)
            logger.info("scheduler_stopped")
        except Exception as exc:  # noqa: BLE001
            logger.error("scheduler_stop_failed", error=str(exc))
    logger.info("shutdown")


app = FastAPI(
    title="UniFi AI Operations Assistant",
    version=settings.APP_VERSION,
    description="AI-powered network operations platform for UniFi infrastructure",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    """Attach a request id / trace id to every request and response."""
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    trace_id = request.headers.get("X-Trace-ID") or request_id
    req_token = request_id_ctx.set(request_id)
    trace_token = trace_id_ctx.set(trace_id)
    try:
        response = await call_next(request)
    except Exception as exc:  # noqa: BLE001 - convert unhandled errors to JSON
        logger.error("unhandled_exception", error=str(exc), path=request.url.path)
        response = JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "detail": str(exc)},
        )
    finally:
        request_id_ctx.reset(req_token)
        trace_id_ctx.reset(trace_token)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Trace-ID"] = trace_id
    return response


app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["root"], summary="Service root")
async def root() -> dict:
    """Return basic service metadata."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "api": "/api/v1",
    }
