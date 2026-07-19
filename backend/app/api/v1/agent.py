"""AI agent chat endpoint with per-user rate limiting."""
import time
from collections import defaultdict, deque

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agent import AgentResponse, NetworkOpsAgent
from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.services import build_services

router = APIRouter(prefix="/agent", tags=["agent"])

# In-memory sliding-window rate limiter: user_id -> deque[timestamps].
_request_log: dict[int, deque] = defaultdict(deque)
_WINDOW_SECONDS = 60


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: list[ChatMessage] = Field(default_factory=list)


def _check_rate_limit(user_id: int) -> None:
    """Enforce a sliding-window rate limit per user."""
    limit = settings.AGENT_RATE_LIMIT_PER_MINUTE
    now = time.monotonic()
    log = _request_log[user_id]
    while log and (now - log[0]) > _WINDOW_SECONDS:
        log.popleft()
    if len(log) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: max {limit} requests per minute",
        )
    log.append(now)


@router.post("/chat", response_model=AgentResponse, summary="Chat with the AI agent")
async def chat(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AgentResponse:
    """Send a message to the read-only AI network operations agent."""
    _check_rate_limit(current_user.id)

    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI agent is not configured (missing OpenAI API key)",
        )

    services = build_services(db)
    agent = NetworkOpsAgent(services)
    history = [m.model_dump() for m in payload.history]
    response = await agent.chat(payload.message, history)
    if response.error and not response.content:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=response.error
        )
    return response
