"""AI Network Operations agent built on the OpenAI API with function calling."""
import json
from typing import Any

from pydantic import BaseModel, Field

from app.ai.tools import TOOL_SCHEMAS, execute_tool
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a senior Network Operations Engineer assistant for a UniFi \
network. You help operators understand and improve their network.

STRICT RULES:
- You NEVER make direct configuration changes. To suggest a change you MUST use the \
`propose_change` tool, which records a proposal for human approval.
- You ONLY use data returned from approved tool calls. NEVER invent, guess, or present \
assumptions as facts.
- You MUST structure every substantive answer into four clearly labeled sections:
  FACTS: objective data retrieved from tools (with source).
  OBSERVATIONS: neutral analysis of the facts.
  RISKS: potential problems, ranked by severity.
  RECOMMENDATIONS: concrete, actionable suggestions (proposals only, never applied).
- If you lack data to answer, say so and call the appropriate tool.
- Be concise, precise, and never overstate certainty.
"""


class AgentResponse(BaseModel):
    """Structured response returned by the agent."""

    content: str = ""
    facts: list[str] = Field(default_factory=list)
    observations: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    tool_calls: list[dict] = Field(default_factory=list)
    error: str | None = None


def _parse_sections(text: str) -> dict[str, list[str]]:
    """Parse FACTS/OBSERVATIONS/RISKS/RECOMMENDATIONS sections from model output."""
    sections: dict[str, list[str]] = {
        "facts": [],
        "observations": [],
        "risks": [],
        "recommendations": [],
    }
    header_map = {
        "FACTS": "facts",
        "OBSERVATIONS": "observations",
        "RISKS": "risks",
        "RECOMMENDATIONS": "recommendations",
    }
    current: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        header = line.rstrip(":").upper()
        matched = None
        for key, target in header_map.items():
            if header == key or line.upper().startswith(key + ":"):
                matched = target
                break
        if matched is not None:
            current = matched
            remainder = line.split(":", 1)[1].strip() if ":" in line else ""
            if remainder:
                sections[current].append(remainder)
            continue
        if current is not None:
            cleaned = line.lstrip("-*• ").strip()
            if cleaned:
                sections[current].append(cleaned)
    return sections


class NetworkOpsAgent:
    """Chat agent that answers questions using read-only network tools."""

    def __init__(self, services: dict, model: str | None = None, client: Any = None):
        self.services = services
        self.model = model or settings.OPENAI_MODEL
        self._client = client
        self.tools = TOOL_SCHEMAS

    @property
    def is_configured(self) -> bool:
        return bool(settings.OPENAI_API_KEY) or self._client is not None

    def _get_client(self):
        if self._client is not None:
            return self._client
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    async def chat(
        self, user_message: str, conversation_history: list[dict] | None = None
    ) -> AgentResponse:
        """Send a message to the agent and return a structured response."""
        if not self.is_configured:
            return AgentResponse(
                error="OpenAI API key is not configured.",
                content="The AI agent is not available because no OpenAI API key is configured.",
            )

        messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        client = self._get_client()
        executed_tool_calls: list[dict] = []

        try:
            for _ in range(6):  # bounded tool-calling loop
                response = await client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                )
                choice = response.choices[0]
                message = choice.message
                tool_calls = getattr(message, "tool_calls", None)

                if not tool_calls:
                    content = message.content or ""
                    sections = _parse_sections(content)
                    return AgentResponse(
                        content=content,
                        facts=sections["facts"],
                        observations=sections["observations"],
                        risks=sections["risks"],
                        recommendations=sections["recommendations"],
                        tool_calls=executed_tool_calls,
                    )

                messages.append(
                    {
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in tool_calls
                        ],
                    }
                )

                for tc in tool_calls:
                    name = tc.function.name
                    try:
                        arguments = json.loads(tc.function.arguments or "{}")
                    except json.JSONDecodeError:
                        arguments = {}
                    try:
                        result = await execute_tool(name, arguments, self.services)
                        result_data = (
                            result.model_dump()
                            if isinstance(result, BaseModel)
                            else self._serialize(result)
                        )
                    except Exception as exc:  # noqa: BLE001 - report tool failures to model
                        result_data = {"error": str(exc)}
                        logger.warning("tool_execution_failed", tool=name, error=str(exc))
                    executed_tool_calls.append({"name": name, "arguments": arguments})
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": json.dumps(result_data, default=str),
                        }
                    )

            return AgentResponse(
                error="Tool call limit reached without a final answer.",
                tool_calls=executed_tool_calls,
            )
        except Exception as exc:  # noqa: BLE001 - surface API errors to the caller
            logger.error("agent_chat_failed", error=str(exc))
            return AgentResponse(error=str(exc), tool_calls=executed_tool_calls)

    @staticmethod
    def _serialize(result: Any) -> Any:
        if isinstance(result, list):
            return [
                r.model_dump() if isinstance(r, BaseModel) else r for r in result
            ]
        return result
