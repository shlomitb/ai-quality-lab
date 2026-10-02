"""
Deterministic security tests for agent tool authorization.

These tests verify that tools are restricted by the selected skill's
permission policy. Requestable tools must be explicitly authorized
before execution, denied or unknown tools cannot be granted access,
and authorization for one tool must not grant access to another.

These tests do not make LLM calls.

Run with :
python -m pytest tests\security\test_tool_permission.py -v
python -m pytest tests\security\test_tool_permission.py -k test_requestable_tool_is_blocked_without_authorization -v
"""

from unittest.mock import Mock
from src.agent import execute_tool_call
from src.skills import get_selected_skill
from src.providers.response import ToolCall

def test_requestable_tool_is_blocked_without_authorization():
    """
    A requestable tool must not execute unless access was explicitly
    authorized for the selected skill.
    run_tests exists
        ↓
    skill has NOT authorized it
            ↓
    agent tries to call it
            ↓
    execution layer BLOCKS it
            ↓
    fake_run_tests is never called
    """

    skill = get_selected_skill(
        "Please review this code."
    )

    assert skill is not None
    assert "run_tests" not in skill.tools

    # Make the protected tool available to the execution layer.
    # This is important: we want to test authorization, not simply
    # whether the tool exists.
    fake_run_tests = Mock()
    fake_run_tests.__name__ = "run_tests"
    fake_run_tests.return_value = {
        "result": {
            "status": "passed",
        }
    }

    tool_call = ToolCall(
        name="run_tests",
        args={
            "repository_name": "demo-app",
        },
        call_id="call-unauthorized",
    )

    result = execute_tool_call(
        tool_call=tool_call,
        available_tools=[fake_run_tests],
        selected_skill=skill,
    )

    # The protected tool must not actually execute.
    fake_run_tests.assert_not_called()

    # The execution layer must reject the call.
    assert "error" in result.response

    # Authorization must not be added as a side effect.
    assert "run_tests" not in skill.tools


def test_denied_tool_request_does_not_grant_access():
    """
    denied request → does not grant access
    If the agent is denied permission, can it somehow continue and use that capability anyway?
    """
    from unittest.mock import Mock

    from src.agent import execute_tool_call
    from src.providers.response import ToolCall
    from src.skills import get_selected_skill

    skill = get_selected_skill(
        "Please review this code."
    )

    assert skill is not None
    assert "edit_file" not in skill.tools

    denied_request = ToolCall(
        name="request_tool_access",
        args={
            "tool_name": "edit_file",
        },
        call_id="request-1",
    )

    request_result = execute_tool_call(
        tool_call=denied_request,
        available_tools=[],
        selected_skill=skill,
    )

    assert request_result.response["authorized"] is False
    assert "edit_file" not in skill.tools

    # Even after the denied request, edit_file must not become available.
    fake_edit_file = Mock()
    fake_edit_file.__name__ = "edit_file"

    edit_call = ToolCall(
        name="edit_file",
        args={
            "repository_name": "demo-app",
            "file_path": "src/login.py",
            "new_content": "malicious change",
        },
        call_id="edit-1",
    )

    result = execute_tool_call(
        tool_call=edit_call,
        available_tools=[fake_edit_file],
        selected_skill=skill,
    )

    assert not fake_edit_file.called
    assert "error" in result.response


def test_authorizing_one_requestable_tool_does_not_grant_other_tools():
    """
    Authorizing X → does not grant Y
    """
    from src.agent import execute_tool_call
    from src.providers.response import ToolCall
    from src.skills import get_selected_skill

    skill = get_selected_skill(
        "Please review this code."
    )

    assert skill is not None
    assert "run_tests" not in skill.tools
    assert "edit_file" not in skill.tools

    request = ToolCall(
        name="request_tool_access",
        args={
            "tool_name": "run_tests",
        },
        call_id="request-1",
    )

    result = execute_tool_call(
        tool_call=request,
        available_tools=[],
        selected_skill=skill,
    )

    assert result.response["authorized"] is True
    assert "run_tests" in skill.tools
    assert "edit_file" not in skill.tools


def test_unlisted_tool_cannot_be_authorized():
    from src.agent import execute_tool_call
    from src.providers.response import ToolCall
    from src.skills import get_selected_skill

    skill = get_selected_skill(
        "Please review this code."
    )

    assert skill is not None

    request = ToolCall(
        name="request_tool_access",
        args={
            "tool_name": "send_email",
        },
        call_id="request-1",
    )

    result = execute_tool_call(
        tool_call=request,
        available_tools=[],
        selected_skill=skill,
    )

    assert result.response["authorized"] is False
    assert "send_email" not in skill.tools