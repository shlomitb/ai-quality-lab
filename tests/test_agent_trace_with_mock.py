
from src.agent import (
    get_tool_calls,
    get_tool_call_details,
    get_tool_result_details,
)
from src.providers.response import AgentResponse, ToolCall, ToolResult
from unittest.mock import Mock, patch

from src.agent import answer_customer_with_trace

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
        }
    ]


def test_agent_passes_selected_skill_tools_to_llm():
    fake_response = Mock()
    fake_response.final_text = "Bug fixed."

    with patch("src.agent.ask_llm", return_value=fake_response) as mock_ask_llm:
        answer_customer_with_trace(
            client=Mock(),
            question="Please investigate BUG-456 and fix the failing test.",
        )

    mock_ask_llm.assert_called_once()

    call_kwargs = mock_ask_llm.call_args.kwargs
    config = call_kwargs["config"]

    tool_names = [tool.__name__ for tool in config.tools]

    assert tool_names == [
        "get_ticket",
        "run_tests",
        "read_file",
        "edit_file",
    ]

def test_agent_adds_run_tests_when_review_requests_it():
    fake_response = Mock()
    fake_response.final_text = "Review completed."

    question = (
        "Please review this code and run the tests to verify your findings."
    )

    with patch(
            "src.agent.ask_llm",
            return_value=fake_response,
    ) as mock_ask_llm:
        answer_customer_with_trace(
            client=Mock(),
            question=question,
        )

    mock_ask_llm.assert_called_once()

    call_kwargs = mock_ask_llm.call_args.kwargs
    config = call_kwargs["config"]

    tool_names = [tool.__name__ for tool in config.tools]

    assert tool_names == [
        "search_files",
        "read_file",
        "run_tests",
    ]