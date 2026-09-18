
from src.agent import (
    answer_customer_with_trace,
    get_tool_calls,
    get_tool_call_details,
    get_tool_result_details,
    execute_tool_call
)
from src.providers.response import AgentResponse, ToolCall, ToolResult
from src.skills import get_selected_skill
from unittest.mock import Mock, patch



"""
Use mock AgentResponse objects to test the agent helper functions
without making an LLM call.
"""


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
        "request_tool_escalation",
    ]



def test_agent_adds_run_tests_when_review_requests_it():
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
        "run_tests",
        "request_tool_escalation",
    ]


def test_execute_tool_call_runs_available_tool():
    from src.agent import execute_tool_call
    from src.providers.response import ToolCall

    tool = Mock()
    tool.__name__ = "run_tests"
    tool.return_value = {"status": "passed"}

    tool_call = ToolCall(
        name="run_tests",
        args={
            "repository_name": "demo-app"
        },
        call_id="call-123",
    )

    result = execute_tool_call(
        tool_call=tool_call,
        available_tools=[tool],
        selected_skill=None,
    )

    tool.assert_called_once_with(
        repository_name="demo-app"
    )

    assert result.name == "run_tests"
    assert result.response == {
        "result": {
            "status": "passed"
        }
    }
    assert result.call_id == "call-123"


def test_execute_tool_call_authorizes_escalation():
    from src.agent import execute_tool_call
    from src.providers.response import ToolCall
    from src.skills import get_selected_skill

    skill = get_selected_skill(
        "Please review this code."
    )

    assert skill is not None
    assert "run_tests" not in skill.tools

    tool_call = ToolCall(
        name="request_tool_escalation",
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



def test_execute_tool_call_denies_unauthorized_escalation():

    skill = get_selected_skill(
        "Please review this code."
    )

    assert skill is not None
    assert "edit_file" not in skill.tools

    tool_call = ToolCall(
        name="request_tool_escalation",
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


def test_agent_handles_dynamic_tool_escalation():

    first_response = AgentResponse(
        final_text="",
        tool_calls=[
            ToolCall(
                name="request_tool_escalation",
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
        "request_tool_escalation",
    ]

    first_send_results = (
        fake_provider.send_tool_results.call_args_list[0]
        .kwargs["tool_results"]
    )

    assert first_send_results[0].name == "request_tool_escalation"
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
        "request_tool_escalation",
    ]

    second_send_results = (
        fake_provider.send_tool_results.call_args_list[1]
        .kwargs["tool_results"]
    )

    assert second_send_results[0].name == "run_tests"
    assert second_send_results[0].response == {
        "result": {
            "status": "passed"
        }
    }


def test_agent_denies_dynamic_unauthorized_escalation():

    first_response = AgentResponse(
        final_text="",
        tool_calls=[
            ToolCall(
                name="request_tool_escalation",
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
    assert send_results[0].name == "request_tool_escalation"
    assert send_results[0].response["tool_name"] == "edit_file"
    assert send_results[0].response["authorized"] is False