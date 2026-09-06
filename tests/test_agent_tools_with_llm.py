import pytest

from src.agent import (answer_customer_with_trace,
                       get_tool_calls,
                       get_tool_call_details,
                       get_tool_result_details)

from src.llm_client import create_client


@pytest.mark.llm
def test_agent_calls_return_policy_tool():
    """Verify that the agent selects the return-policy tool."""
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="Can I return an opened product after 20 days if defective?"
    )

    tool_calls = get_tool_calls(response)

    print(tool_calls)

    assert tool_calls == ["get_return_policy"]


@pytest.mark.llm
def test_agent_selects_product_information_tool():
    """Verify that the agent selects the product-information tool."""
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What is the price of the Example Product?"
    )

    tool_calls = get_tool_calls(response)

    assert tool_calls == ["get_product_information"]


@pytest.mark.llm
def test_agent_passes_correct_product_name():
    """Verify that the agent passes the correct product name to the tool."""
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What is the price of the Example Product?"
    )

    tool_call_details = get_tool_call_details(response)

    assert tool_call_details == [
        {
            "name": "get_product_information",
            "args": {
                "product_name": "Example Product"
            }
        }
    ]


@pytest.mark.llm
def test_agent_receives_expected_product_information():
    """Verify that the expected product information appears in the tool result."""
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What is the price of the Example Product?"
    )

    tool_results = get_tool_result_details(response)

    assert tool_results == [
        {
            "name": "get_product_information",
            "response": {
                "result": {
                    "category": "physical",
                    "name": "Example Product",
                    "price": 49.99
                }
            }
        }
    ]