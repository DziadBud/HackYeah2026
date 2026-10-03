from collections.abc import Callable, Sequence
from typing import Any

from pydantic_ai import Agent, Tool
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from app.config import settings
from app.services.llm.errors import LlmError


def build_gemini_model() -> GoogleModel:
    if not settings.gemini_api_key:
        raise LlmError("GEMINI_API_KEY is not set")
    return GoogleModel(
        settings.gemini_model,
        provider=GoogleProvider(api_key=settings.gemini_api_key),
    )


def create_agent(
    *,
    output_type: Any = str,
    system_prompt: str | Sequence[str] = (),
    tools: Sequence[Callable[..., Any] | Tool[Any]] = (),
    mcp_servers: Sequence[str] = (),
    name: str | None = None,
) -> Agent[Any, Any]:
    """Build a Gemini agent with optional structured output, tools (skills), and MCP.

    Example:
        class MatchReason(BaseModel):
            summary: str
            score: float

        agent = create_agent(
            output_type=MatchReason,
            system_prompt="Explain matches using only provided facts.",
            tools=[lookup_innovation],
            mcp_servers=["http://localhost:8002/mcp"],
        )
        result = agent.run_sync("Why does X fit Y?")
        reason = result.output  # MatchReason
    """
    toolsets = [MCPToolset(server) for server in mcp_servers]
    return Agent(
        build_gemini_model(),
        output_type=output_type,
        system_prompt=system_prompt,
        tools=tools,
        toolsets=toolsets or None,
        name=name,
    )
