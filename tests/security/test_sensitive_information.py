

from src import agent, tools
from src.agent import execute_tool_call
from src.providers.response import AgentResponse, ToolCall
from src.security import (
    SENSITIVE_FIELDS,
    redact_sensitive_values,
    sanitize_ticket,
)
from src.skills import SelectedSkill




def test_final_response_does_not_leak_internal_notes():
    """
    Final agent response cannot expose a known secret
    """
    sensitive_value = "INTERNAL-ONLY-12345"

    response = AgentResponse(
        final_text=f"The ticket contains: {sensitive_value}",
        tool_calls=[],
        tool_results=[],
        parsed=None,
    )

    safe_response = agent.filter_sensitive_information(response)

    assert sensitive_value not in safe_response.final_text


def test_internal_notes_is_a_sensitive_field():
    """
    Configuration contains the expected sensitive field
    """
    assert "internal_notes" in SENSITIVE_FIELDS


def test_sanitize_ticket_removes_sensitive_fields():
    """
    Explicit sensitive fields are removed
    """
    ticket = {
        "ticket_id": "BUG-SECRET",
        "title": "Login issue",
        "description": "Login fails.",
        "repository": "demo-app",
        "status": "Open",
        "internal_notes": "INTERNAL-ONLY-12345",
    }

    sanitized = sanitize_ticket(ticket)

    assert "internal_notes" not in sanitized
    assert "INTERNAL-ONLY-12345" not in sanitized.values()

    assert sanitized["ticket_id"] == "BUG-SECRET"
    assert sanitized["title"] == "Login issue"


def test_get_ticket_does_not_pass_sensitive_fields_to_agent():
    """
    Very strong test, verifies that the sensitive field/value is gone.
    End-to-end deterministic boundary: get_ticket → execute_tool_call → agent result
    """
    ticket = {
        "ticket_id": "BUG-SECRET",
        "title": "Login issue",
        "description": "Login fails.",
        "repository": "demo-app",
        "status": "Open",
        "internal_notes": "INTERNAL-ONLY-12345",
    }

    tools.tickets["BUG-SECRET"] = ticket

    try:
        tool_call = ToolCall(
            name="get_ticket",
            args={"ticket_id": "BUG-SECRET"},
            call_id="test-call-1",
        )

        selected_skill = SelectedSkill(
            name="investigate-bug",
            instructions="",
            tools=["get_ticket"],
        )

        result = execute_tool_call(
            tool_call=tool_call,
            available_tools=[tools.get_ticket],
            selected_skill=selected_skill,
        )

        result_text = str(result.response)

        assert "INTERNAL-ONLY-12345" not in result_text
        assert "internal_notes" not in result_text

        assert "BUG-SECRET" in result_text
        assert "Login issue" in result_text

    finally:
        del tools.tickets["BUG-SECRET"]


def test_sanitize_ticket_does_not_modify_original_ticket():
    """
    Good defensive-programming test.
    The sanitizer shouldn't unexpectedly mutate the source object.
    """
    ticket = {
        "ticket_id": "BUG-SECRET",
        "title": "Login issue",
        "internal_notes": "INTERNAL-ONLY-12345",
    }

    original_ticket = ticket.copy()

    sanitized = sanitize_ticket(ticket)

    assert ticket == original_ticket
    assert "internal_notes" in ticket
    assert "internal_notes" not in sanitized



def test_sanitize_ticket_redacts_secret_inside_unclassified_field():
    """
    Secret values are caught even when field isn't classified
    """
    ticket = {
        "ticket_id": "BUG-789",
        "title": "Login issue",
        "description": "Temporary password: Temp#4729",
        "repository": "demo-app",
        "status": "Open",
    }

    sanitized = sanitize_ticket(ticket)

    assert "Temp#4729" not in str(sanitized)



def test_redact_sensitive_values_removes_password_value():
    """
    Good focused unit test of the password-redaction function.
    """
    text = "Temporary password: Temp#4729"

    redacted = redact_sensitive_values(text)

    assert redacted == "Temporary password: [REDACTED]"



def test_sanitize_ticket_redacts_password_in_description():
    """
    Tests the next layer: the ticket sanitizer uses the redaction mechanism correctly.
    """
    ticket = {
        "ticket_id": "BUG-789",
        "title": "Login issue",
        "description": "Temporary password: Temp#4729",
        "repository": "demo-app",
        "status": "Open",
    }

    sanitized = sanitize_ticket(ticket)

    assert sanitized["description"] == (
        "Temporary password: [REDACTED]"
    )


def test_unclassified_secret_is_redacted_before_agent_receives_tool_result():
    """
    Very strong testpytest -v tests/security/test_sensitive_information.py
    End-to-end deterministic redaction boundary
    Verify that secret values in unclassified fields are redacted
    before the tool result reaches the agent.
    """
    ticket = {
        "ticket_id": "BUG-789",
        "title": "Login issue",
        "description": "Temporary password: Temp#4729",
        "repository": "demo-app",
        "status": "Open",
    }

    tools.tickets["BUG-789"] = ticket

    try:
        tool_call = ToolCall(
            name="get_ticket",
            args={"ticket_id": "BUG-789"},
            call_id="test-secret-1",
        )

        selected_skill = SelectedSkill(
            name="investigate-bug",
            instructions="",
            tools=["get_ticket"],
        )

        result = execute_tool_call(
            tool_call=tool_call,
            available_tools=[tools.get_ticket],
            selected_skill=selected_skill,
        )

        result_text = str(result.response)

        assert "Temp#4729" not in result_text
        assert "Temporary password: [REDACTED]" in result_text

    finally:
        del tools.tickets["BUG-789"]