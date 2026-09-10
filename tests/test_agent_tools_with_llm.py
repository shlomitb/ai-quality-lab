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


@pytest.mark.llm
def test_agent_handles_product_information_failure():
    """
    An LLM integration test.
    The LLM responded with the expected error, and it did not hallucinate a price
    :return:
    """
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What is the price of the Unavailable Product?",
    )

    tool_results = get_tool_result_details(response)

    assert tool_results == [
        {
            "name": "get_product_information",
            "response": {
                "result": {
                    "result": {
                        "error": "Product information service is temporarily unavailable."
                    }
                }
            }
        }
    ]

    assert "49.99" not in response.text


@pytest.mark.llm
def test_agent_recovers_from_product_information_failure():
    """
    Testing that the agent calls 2 tools, in the order we specified.
    We expect the 1st tool to fail and due to that the 2nd tool to be called
    This is testing that the agent knows how to recover from a failure.
    """
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What is the price of the Unavailable Product?",
    )

    tool_call_details = get_tool_call_details(response)

    assert tool_call_details == [
        {
            "name": "get_product_information",
            "args": {
                "product_name": "Unavailable Product",
            },
        },
        {
            "name": "search_product_catalog",
            "args": {
                "product_name": "Unavailable Product",
            },
        },
    ]

    assert "49.99" in response.text


@pytest.mark.llm
def test_agent_handles_both_product_information_tools_failing():
    """
    Run with -s if want to see the prints:
    pytest -v -s --run-llm tests/test_agent_tools_with_llm.py -k both_product_information_tools_failing
    """
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What is the price of the Unknown Product?",
    )

    tool_call_details = get_tool_call_details(response)

    #checks that the real LLM tried get_product_information and tehn  whe it failed tried search_product_catalog
    #and in both it passed the  correct product name
    assert tool_call_details == [
        {
            "name": "get_product_information",
            "args": {
                "product_name": "Unknown Product",
            },
        },
        {
            "name": "search_product_catalog",
            "args": {
                "product_name": "Unknown Product",
            },
        },
    ]

    # print("\nTOOL CALLS:")
    # print(tool_call_details)

    tool_results = get_tool_result_details(response)

    # print("\nTOOL RESULTS:")
    # print(tool_results)

    assert len(tool_results) == 2

    #checks that the agent did not invent the price when neither tool could provide it
    assert "49.99" not in response.text

    # print("\nFINAL RESPONSE:")
    # print(response.text)