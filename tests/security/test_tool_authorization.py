"""
Tests the agent's runtime tool-authorization layer and verifies that unauthorized tool calls are blocked.
"""

from unittest.mock import Mock


def test_execute_tool_call_blocks_unauthorized_tool():
    """
    A tool can exist and even be passed to execute_tool_call(), but if the selected skill isn't authorized for it, the application blocks execution.
    review-code
    ↓
    attempts simulate_sensitive_action
        ↓
    BLOCKED
    """
    from src.agent import execute_tool_call
    from src.providers.response import ToolCall
    from src.skills import SelectedSkill

    tool = Mock()
    tool.__name__ = "simulate_sensitive_action"
    tool.return_value = "Sensitive action executed."

    tool_call = ToolCall(
        name="simulate_sensitive_action",
        args={},
        call_id="call-security-123",
    )

    selected_skill = SelectedSkill(
        name="review-code",
        instructions="",
        tools=["search_files", "read_file"],
    )

    result = execute_tool_call(
        tool_call=tool_call,
        available_tools=[tool],
        selected_skill=selected_skill,
    )

    tool.assert_not_called()

    assert result.name == "simulate_sensitive_action"
    assert result.response == {
        "error": "Tool is not authorized."
    }
    assert result.call_id == "call-security-123"
