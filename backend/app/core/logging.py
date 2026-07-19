"""Structured JSON logging configuration using structlog."""
import logging
import sys
from contextvars import ContextVar

import structlog

from app.core.config import settings

# Context variables populated by middleware for request correlation.
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")
trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="-")

_configured = False


def _add_request_context(logger, method_name, event_dict):
    """Inject request_id and trace_id from context vars into every log entry."""
    event_dict["request_id"] = request_id_ctx.get()
    event_dict["trace_id"] = trace_id_ctx.get()
    return event_dict


def configure_logging() -> None:
    """Configure structlog to emit structured JSON logs."""
    global _configured
    if _configured:
        return

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            _add_request_context,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    _configured = True


def get_logger(name: str) -> structlog.BoundLogger:
    """Return a structlog bound logger for the given name."""
    if not _configured:
        configure_logging()
    return structlog.get_logger(name)
