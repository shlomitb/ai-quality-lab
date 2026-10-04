"""
General deterministic agent-loop and trace tests.

Use mocked providers and AgentResponse objects to test the agent's
tool execution, dynamic tool access, and trace helpers without
making real LLM/API calls.
"""
from unittest.mock import Mock, patch

from src.agent import (
    answer_customer_with_trace,
    enforce_tool_result_consistency,
    execute_tool_call,
    get_tool_calls,
    get_tool_call_details,
    get_tool_result_details,
    MAX_AGENT_TURNS,
    _find_tool,
    _handle_tool_access_request,
    _sanitize_tool_result,
)
from src.providers.response import AgentResponse, ToolCall, ToolResult
from src.skills import get_selected_skill, SelectedSkill



def test_find_tool_returns_matching_tool():
    def fake_tool():
        pass

    fake_tool.__name__ = "fake_tool"

    result = _find_tool(
        "fake_tool",
        [fake_tool],
    )

    assert result is fake_tool



def test_handle_tool_access_request_authorizes_requestable_tool():
    selected_skill = Mock()
    selected_skill.name = "review-code"
    selected_skill.tools = [
        "search_files",
        "read_file",
        "request_tool_access",
    ]

    tool_call = ToolCall(
        name="request_tool_access",
        args={"tool_name": "run_tests"},
        call_id="call-helper-test",
    )

    result = _handle_tool_access_request(
        tool_call,
        selected_skill,
    )

    assert result.name == "request_tool_access"
    assert result.response == {
        "tool_name": "run_tests",
        "authorized": True,
    }

    assert "run_tests" in selected_skill.tools


def test_sanitize_tool_result_removes_sensitive_ticket_fields():
    response = {
        "result": {
            "ticket_id": "BUG-SECRET",
            "title": "Login issue",
            "internal_notes": "INTERNAL-ONLY-12345",
        }
    }

    result = _sanitize_tool_result(
        "get_ticket",
        response,
    )

    assert result == {
        "result": {
            "ticket_id": "BUG-SECRET",
            "title": "Login issue",
        }
    }

    assert "INTERNAL-ONLY-12345" not in str(result)

def test_get_tool_calls():
    """
    Test that get_tool_calls() extracts one tool name
    from an AgentResponse.
    """

    response = AgentResponse(
        final_text="",
        tool_calls=[
            ToolCall(
                name="get_return_policy",
                args={},
            )
        ],
    )

    tool_calls = get_tool_calls(response)

    assert tool_calls == ["get_return_policy"]


def test_get_tool_calls_pass_no_tools():
    response = AgentResponse(
        final_text="",
        tool_calls=[],
    )

    tool_calls = get_tool_calls(response)

    assert tool_calls == []


def test_get_tool_calls_with_two_tools():
    """
    Test that get_tool_calls() extracts two tool names
    in the correct order.
    """

    response = AgentResponse(
        final_text="",
        tool_calls=[
            ToolCall(
                name="tool1",
                args={},
            ),
            ToolCall(
                name="tool2",
                args={},
            ),
        ],
    )

    tool_calls = get_tool_calls(response)

    assert tool_calls == ["tool1", "tool2"]


def test_get_tool_call_details_with_arguments():
    response = AgentResponse(
        final_text="",
        tool_calls=[
            ToolCall(
                name="get_product_information",
                args={
                    "product_name": "Example Product"
                },
            )
        ],
    )

    tool_call_details = get_tool_call_details(response)

    assert tool_call_details == [
        {
            "name": "get_product_information",
            "args": {
                "product_name": "Example Product"
            },
            "call_id": None,
        }
    ]


def test_get_tool_result_details():
    response = AgentResponse(
        final_text="",
        tool_results=[
            ToolResult(
                name="get_product_information",
                response={
                    "result": {
                        "category": "physical",
                        "name": "Example Product",
                        "price": 49.99,
                    }
                },
            )
        ],
    )

    tool_results = get_tool_result_details(response)

    assert tool_results == [
        {
            "name": "get_product_information",
            "response": {
                "result": {
                    "category": "physical",
                    "name": "Example Product",
                    "price": 49.99,
                }
            },
            "call_id": None,
        }
    ]


def test_agent_passes_selected_skill_tools_to_llm():
    fake_response = Mock()
    fake_response.final_text = "Bug fixed."
    fake_response.tool_calls = []
    fake_response.tool_results = []

    fake_provider = Mock()
    fake_provider.generate.return_value = fake_response

    with patch(
        "src.agent.create_provider",
        return_value=fake_provider,
    ):
        answer_customer_with_trace(
            client=Mock(),
            question="Please investigate BUG-456 and fix the failing test.",
        )

    fake_provider.generate.assert_called_once()

    call_kwargs = fake_provider.generate.call_args.kwargs
    config = call_kwargs["config"]

    tool_names = [tool.__name__ for tool in config.tools]

    assert tool_names == [
        "get_ticket",
        "run_tests",
        "read_file",
        "edit_file",
        "request_tool_access",
    ]



def test_agent_does_not_initially_add_requestable_tool():
    fake_response = Mock()
    fake_response.final_text = "Review completed."
    fake_response.tool_calls = []
    fake_response.tool_results = []

    fake_provider = Mock()
    fake_provider.generate.return_value = fake_response

    question = (
        "Please review this code and run the tests "
        "to verify your findings."
    )

    with patch(
            "src.agent.create_provider",
            return_value=fake_provider,
    ):
        answer_customer_with_trace(
            client=Mock(),
            question=question,
        )

    fake_provider.generate.assert_called_once()

    call_kwargs = fake_provider.generate.call_args.kwargs
    config = call_kwargs["config"]

    tool_names = [tool.__name__ for tool in config.tools]

    assert tool_names == [
        "search_files",
        "read_file",
        "request_tool_access",
    ]


def test_execute_tool_call_runs_available_tool():
    mock_tool = Mock()
    mock_tool.__name__ = "run_tests"
    mock_tool.return_value = {"status": "passed"}

    tool_call = ToolCall(
        name="run_tests",
        args={"repository_name": "demo-app"},
        call_id="call-123",
    )

    selected_skill = Mock()
    selected_skill.name = "investigate-bug"
    selected_skill.tools = ["run_tests"]

    result = execute_tool_call(
        tool_call=tool_call,
        available_tools=[mock_tool],
        selected_skill=selected_skill,
    )

    mock_tool.assert_called_once_with(
        repository_name="demo-app"
    )

    assert result.name == "run_tests"
    assert result.response == {
        "status": "passed"
    }
    assert result.call_id == "call-123"



def test_execute_tool_call_authorizes_tool_access_request():
    skill = get_selected_skill(
        "Please review this code."
    )

    assert skill is not None
    assert "run_tests" not in skill.tools

    tool_call = ToolCall(
        name="request_tool_access",
        args={
            "tool_name": "run_tests"
        },
        call_id="call-456",
    )

    result = execute_tool_call(
        tool_call=tool_call,
        available_tools=[],
        selected_skill=skill,
    )

    assert result.response["authorized"] is True
    assert result.response["tool_name"] == "run_tests"
    assert "run_tests" in skill.tools



def test_execute_tool_call_denies_unauthorized_tool_access_request():
    skill = get_selected_skill(
        "Please review this code."
    )

    assert skill is not None
    assert "edit_file" not in skill.tools

    tool_call = ToolCall(
        name="request_tool_access",
        args={
            "tool_name": "edit_file"
        },
        call_id="call-789",
    )

    result = execute_tool_call(
        tool_call=tool_call,
        available_tools=[],
        selected_skill=skill,
    )

    assert result.response["authorized"] is False
    assert "edit_file" not in skill.tools


def test_agent_handles_dynamic_tool_access():
    first_response = AgentResponse(
        final_text="",
        tool_calls=[
            ToolCall(
                name="request_tool_access",
                args={
                    "tool_name": "run_tests"
                },
                call_id="call-1",
            )
        ],
        tool_results=[],
    )

    second_response = AgentResponse(
        final_text="",
        tool_calls=[
            ToolCall(
                name="run_tests",
                args={
                    "repository_name": "demo-app"
                },
                call_id="call-2",
            )
        ],
        tool_results=[],
    )

    final_response = AgentResponse(
        final_text="The review is complete. The tests passed.",
        tool_calls=[],
        tool_results=[],
    )

    fake_provider = Mock()

    fake_provider.generate.return_value = first_response

    fake_provider.send_tool_results.side_effect = [
        second_response,
        final_response,
    ]

    fake_run_tests = Mock(
        return_value={
            "status": "passed"
        }
    )

    fake_run_tests.__name__ = "run_tests"

    with patch(
        "src.agent.create_provider",
        return_value=fake_provider,
    ):
        with patch.dict(
                "src.tool_catalog.TOOLS",
                {"run_tests": fake_run_tests},
                clear=False,
        ):
            response = answer_customer_with_trace(
                client=Mock(),
                question="Please review this code.",
            )

    assert response.final_text == (
        "The review is complete. The tests passed."
    )

    fake_provider.generate.assert_called_once()
    assert fake_provider.send_tool_results.call_count == 2

    fake_run_tests.assert_called_once_with(
        repository_name="demo-app"
    )

    first_config = fake_provider.generate.call_args.kwargs["config"]

    first_tool_names = [
        tool.__name__
        for tool in first_config.tools
    ]

    assert first_tool_names == [
        "search_files",
        "read_file",
        "request_tool_access",
    ]

    first_send_results = (
        fake_provider.send_tool_results.call_args_list[0]
        .kwargs["tool_results"]
    )

    assert first_send_results[0].name == "request_tool_access"
    assert first_send_results[0].response["tool_name"] == "run_tests"
    assert first_send_results[0].response["authorized"] is True

    second_config = (
        fake_provider.send_tool_results.call_args_list[0]
        .kwargs["config"]
    )

    second_tool_names = [
        tool.__name__
        for tool in second_config.tools
    ]

    assert second_tool_names == [
        "search_files",
        "read_file",
        "run_tests",
        "request_tool_access",
    ]

    second_send_results = (
        fake_provider.send_tool_results.call_args_list[1]
        .kwargs["tool_results"]
    )

    assert second_send_results[0].name == "run_tests"

    assert second_send_results[0].response == {
        "status": "passed"
    }


def test_agent_denies_unauthorized_dynamic_tool_access():

    first_response = AgentResponse(
        final_text="",
        tool_calls=[
            ToolCall(
                name="request_tool_access",
                args={
                    "tool_name": "edit_file"
                },
                call_id="call-1",
            )
        ],
        tool_results=[],
    )

    final_response = AgentResponse(
        final_text="I cannot make that change because it is not authorized.",
        tool_calls=[],
        tool_results=[],
    )

    fake_provider = Mock()
    fake_provider.generate.return_value = first_response
    fake_provider.send_tool_results.return_value = final_response

    with patch(
        "src.agent.create_provider",
        return_value=fake_provider,
    ):
        response = answer_customer_with_trace(
            client=Mock(),
            question="Please review this code.",
        )

    assert response.final_text == (
        "I cannot make that change because it is not authorized."
    )

    fake_provider.generate.assert_called_once()
    fake_provider.send_tool_results.assert_called_once()

    send_results = (
        fake_provider.send_tool_results.call_args.kwargs[
            "tool_results"
        ]
    )

    second_config = (
        fake_provider.send_tool_results.call_args.kwargs["config"]
    )

    second_tool_names = [
        tool.__name__
        for tool in second_config.tools
    ]

    assert "edit_file" not in second_tool_names
    assert send_results[0].name == "request_tool_access"
    assert send_results[0].response["tool_name"] == "edit_file"
    assert send_results[0].response["authorized"] is False



def test_agent_stops_after_max_agent_turns():
    """
    Verify that the agent stops executing tool calls when
    MAX_AGENT_TURNS is reached, even if the provider keeps
    requesting another tool call.
    """
    tool_response = AgentResponse(
        final_text="",
        tool_calls=[
            ToolCall(
                name="get_ticket",
                args={"ticket_id": "BUG-123"},
                call_id="call-1",
            )
        ],
        tool_results=[],
    )

    fake_provider = Mock()

    # Initial model response contains a tool call.
    fake_provider.generate.return_value = tool_response

    # Every subsequent model response also contains a tool call.
    fake_provider.send_tool_results.return_value = tool_response

    with patch(
        "src.agent.create_provider",
        return_value=fake_provider,
    ):
        with patch(
            "src.agent.MAX_AGENT_TURNS",
            3,
        ):
            response = answer_customer_with_trace(
                client=Mock(),
                question="Investigate BUG-123.",
            )

    assert fake_provider.generate.call_count == 1
    assert fake_provider.send_tool_results.call_count == 3

    # The agent received another tool call at the final turn,
    # but did not execute another turn after reaching the limit.
    assert response.tool_calls



def test_request_tool_access_requires_tool_name():
    skill = get_selected_skill(
        "Please review this code."
    )

    assert skill is not None

    tool_call = ToolCall(
        name="request_tool_access",
        args={},
        call_id="call-missing",
    )

    result = execute_tool_call(
        tool_call=tool_call,
        available_tools=[],
        selected_skill=skill,
    )

    assert result.name == "request_tool_access"
    assert result.response == {
        "error": "tool_name is required."
    }


def test_request_tool_access_rejects_non_string_tool_name():
    skill = get_selected_skill(
        "Please review this code."
    )

    assert skill is not None

    tool_call = ToolCall(
        name="request_tool_access",
        args={
            "tool_name": 123
        },
        call_id="call-invalid-type",
    )

    result = execute_tool_call(
        tool_call=tool_call,
        available_tools=[],
        selected_skill=skill,
    )

    assert result.name == "request_tool_access"
    assert result.response == {
        "error": "tool_name is required."
    }

def test_request_tool_access_denied_when_no_skill_is_selected():
    tool_call = ToolCall(
        name="request_tool_access",
        args={
            "tool_name": "run_tests"
        },
        call_id="call-no-skill",
    )

    result = execute_tool_call(
        tool_call=tool_call,
        available_tools=[],
        selected_skill=None,
    )

    assert result.name == "request_tool_access"
    assert result.response == {
        "error": "No skill is selected; tool access denied."
    }


def test_agent_returns_failure_message_when_max_turns_reached():
    """
    agent keeps requesting tools
        ↓
    MAX_AGENT_TURNS reached
        ↓
    agent terminates
        ↓
    final_text is non-empty
        ↓
    explicit failure message returned

    It also verifies the loop doesn't silently stop in a broken state.
    """
    repeated_tool_call = ToolCall(
        name="get_ticket",
        args={"ticket_id": "BUG-456"},
        call_id="test-call",
    )

    initial_response = AgentResponse(
        final_text="",
        tool_calls=[repeated_tool_call],
        tool_results=[],
        parsed=None,
    )

    repeated_response = AgentResponse(
        final_text="",
        tool_calls=[repeated_tool_call],
        tool_results=[],
        parsed=None,
    )

    fake_provider = Mock()
    fake_provider.generate.return_value = initial_response
    fake_provider.send_tool_results.return_value = repeated_response

    with patch(
        "src.agent.create_provider",
        return_value=fake_provider,
    ):
        response = answer_customer_with_trace(
            client=Mock(),
            question="Please investigate BUG-456 and fix the failing test.",
        )

    assert fake_provider.generate.call_count == 1
    assert (
        fake_provider.send_tool_results.call_count
        == MAX_AGENT_TURNS
    )

    assert len(response.tool_calls) == MAX_AGENT_TURNS + 1
    assert response.final_text == (
        "I could not complete the request because the agent "
        "reached its maximum number of turns."
    )


def test_agent_does_not_report_success_when_tests_fail():
    failed_test_result = ToolResult(
        name="run_tests",
        response={
            "result": {
                "result": {
                    "status": "failed",
                    "tests_run": 1,
                    "tests_failed": 1,
                }
            }
        },
        call_id="test-call",
    )

    response = AgentResponse(
        final_text="The tests passed successfully.",
        tool_calls=[],
        tool_results=[failed_test_result],
        parsed=None,
    )

    safe_response = enforce_tool_result_consistency(response)

    assert safe_response.final_text == (
        "The tests failed, so I cannot report the "
        "verification as successful."
    )


def test_enforce_tool_result_consistency_rejects_success_after_failed_tests():
    failed_test_result = ToolResult(
        name="run_tests",
        response={
            "result": {
                "result": {
                    "status": "failed",
                    "tests_run": 1,
                    "tests_failed": 1,
                }
            }
        },
        call_id="test-call",
    )

    response = AgentResponse(
        final_text="The tests passed successfully.",
        tool_calls=[],
        tool_results=[failed_test_result],
        parsed=None,
    )

    safe_response = enforce_tool_result_consistency(response)

    assert safe_response.final_text == (
        "The tests failed, so I cannot report the "
        "verification as successful."
    )


def test_enforce_tool_result_consistency_keeps_success_after_passed_tests():
    passed_test_result = ToolResult(
        name="run_tests",
        response={
            "result": {
                "result": {
                    "status": "passed",
                    "tests_run": 1,
                    "tests_failed": 0,
                }
            }
        },
        call_id="test-call",
    )

    response = AgentResponse(
        final_text="The tests passed successfully.",
        tool_calls=[],
        tool_results=[passed_test_result],
        parsed=None,
    )

    safe_response = enforce_tool_result_consistency(response)

    assert safe_response is response


def test_enforce_tool_result_consistency_ignores_other_tool_results():
    read_result = ToolResult(
        name="read_file",
        response={
            "result": {
                "result": {
                    "content": "some source code"
                }
            }
        },
        call_id="test-call",
    )

    response = AgentResponse(
        final_text="The code looks good.",
        tool_calls=[],
        tool_results=[read_result],
        parsed=None,
    )

    safe_response = enforce_tool_result_consistency(response)

    assert safe_response is response


def test_enforce_tool_result_consistency_uses_latest_test_result():
    failed_test_result = ToolResult(
        name="run_tests",
        response={
            "result": {
                "result": {
                    "status": "failed",
                    "tests_run": 1,
                    "tests_failed": 1,
                }
            }
        },
        call_id="failed-call",
    )

    passed_test_result = ToolResult(
        name="run_tests",
        response={
            "result": {
                "result": {
                    "status": "passed",
                    "tests_run": 1,
                    "tests_failed": 0,
                }
            }
        },
        call_id="passed-call",
    )

    response = AgentResponse(
        final_text="The tests passed successfully.",
        tool_calls=[],
        tool_results=[
            failed_test_result,
            passed_test_result,
        ],
        parsed=None,
    )

    safe_response = enforce_tool_result_consistency(response)

    assert safe_response is response
