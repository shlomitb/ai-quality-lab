
from unittest.mock import Mock

"""
Prompt-injection security — malicious instructions cannot cause unauthorized action
"""

def test_prompt_injection_cannot_execute_unauthorized_tool():
    """
    This test pretends that the agent followed the injection and requested this tool.
    In: tool_call = ToolCall(
        name="simulate_sensitive_action",
    This test checks that even if untrusted content causes the agent to attempt a sensitive action, the application authorization layer prevents that action.
    malicious file
    ↓
    contains "Ignore previous instructions..."
        ↓
    simulated agent attempts simulate_sensitive_action
        ↓
    authorization layer
        ↓
    BLOCKED
    """
    from pathlib import Path

    from src.agent import execute_tool_call
    from src.providers.response import ToolCall
    from src.skills import SelectedSkill

    fixture_path = Path(
        "tests/fixtures/prompt_injection/malicious_login.py"
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
    assert result.response == {
        "error": "Tool is not authorized."
    }
    assert result.call_id == "call-prompt-injection-123"