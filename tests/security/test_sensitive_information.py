


from src import agent
from src import tools
from src.agent import execute_tool_call
from src.providers.response import AgentResponse, ToolCall
from src.security import SENSITIVE_FIELDS, sanitize_ticket
from src.skills import SelectedSkill
from src.tools import get_ticket


def test_get_ticket_exposes_internal_notes():
    ticket = {
        "ticket_id": "BUG-SECRET",
        "title": "Login issue",
        "description": "Login fails.",
        "repository": "demo-app",
        "status": "Open",
        "internal_notes": "INTERNAL-ONLY-12345",
    }

    # Temporarily add our security test ticket.
    from src import tools

    tools.tickets["BUG-SECRET"] = ticket

    try:
        result = get_ticket("BUG-SECRET")

        assert result["result"]["internal_notes"] == "INTERNAL-ONLY-12345"
    finally:
        del tools.tickets["BUG-SECRET"]


def test_final_response_does_not_leak_internal_notes():
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
    assert "internal_notes" in SENSITIVE_FIELDS


def test_sanitize_ticket_removes_sensitive_fields():
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


def test_sensitive_fields_are_removed_before_agent_receives_ticket():
    ticket = {
        "ticket_id": "BUG-SECRET",
        "title": "Login issue",
        "description": "Login fails.",
        "repository": "demo-app",
        "status": "Open",
        "internal_notes": "INTERNAL-ONLY-12345",
    }

    from src import tools
    tools.tickets["BUG-SECRET"] = ticket

    try:
        result = get_ticket("BUG-SECRET")

        raw_ticket = result["result"]
        safe_ticket = sanitize_ticket(raw_ticket)

        assert "internal_notes" not in safe_ticket
        assert "INTERNAL-ONLY-12345" not in str(safe_ticket)

        assert safe_ticket["ticket_id"] == "BUG-SECRET"
        assert safe_ticket["title"] == "Login issue"

    finally:
        del tools.tickets["BUG-SECRET"]


def test_get_ticket_does_not_pass_sensitive_fields_to_agent():
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