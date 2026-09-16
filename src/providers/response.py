from dataclasses import dataclass, field
from typing import Any

@dataclass
class ToolCall:
    """
    name: the tool did the agent ask to call
    args: the arguments for the tool
    ex:
    ToolCall(
        name="get_ticket",
        args={"ticket_id": "BUG-456"}
    )
    """
    name: str
    args: dict


@dataclass
class ToolResult:
    """
    Represents:
    name: what tool ran
    response: the result that the tool returned
    """
    name: str
    response: dict


@dataclass
class AgentResponse:
    final_text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_results: list[ToolResult] = field(default_factory=list)
    parsed: Any | None = None