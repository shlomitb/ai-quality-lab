
from src.agent import (
    get_tool_calls,
    get_tool_call_details,
    get_tool_result_details,
)
from src.providers.response import AgentResponse, ToolCall, ToolResult


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
