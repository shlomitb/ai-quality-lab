"""
Prompt-injection security — malicious instructions cannot cause unauthorized action

Even when malicious content causes an attempted call to simulate_sensitive_action,
the application authorization layer blocks the tool because that tool is not authorized for the selected skill.
"""

from pathlib import Path

from src.agent import execute_tool_call
from src.providers.response import ToolCall
from src.skills import SelectedSkill
from unittest.mock import Mock


def test_prompt_injection_cannot_execute_unauthorized_tool():
    """
    Verify that the authorization layer blocks a sensitive tool even when
    untrusted content causes the agent to attempt that tool.

    This test simulates the agent already following the malicious instruction.
    It therefore tests the application-level security boundary, not whether
    the LLM itself resists prompt injection.
    """

    fixture_path = (
            Path(__file__).parents[1]
            / "fixtures"
            / "prompt_injection"
            / "malicious_login.py"
    )

    malicious_content = fixture_path.read_text()

    assert "Ignore previous instructions." in malicious_content
    assert "simulate_sensitive_action" in malicious_content

    sensitive_tool = Mock()
    sensitive_tool.__name__ = "simulate_sensitive_action"
    sensitive_tool.return_value = "Sensitive action executed."

    tool_call = ToolCall(
        name="simulate_sensitive_action",
        args={},
        call_id="call-prompt-injection-123",
    )

    selected_skill = SelectedSkill(
        name="review-code",
        instructions="",
        tools=["search_files", "read_file"],
    )

    result = execute_tool_call(
        tool_call=tool_call,
        available_tools=[sensitive_tool],
        selected_skill=selected_skill,
    )

    sensitive_tool.assert_not_called()

    assert result.name == "simulate_sensitive_action"
    assert result.response["error"].startswith(
        "Tool 'simulate_sensitive_action' is not authorized"
    )
    assert result.call_id == "call-prompt-injection-123"