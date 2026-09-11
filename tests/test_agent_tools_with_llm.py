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


@pytest.mark.llm
def test_agent_uses_order_information_to_check_return_eligibility():
    """
    We are teting here that the llm chooses to 1st call tool "get_order_information"
    since it has the order id and needs the details in this tool call response
    in order to call the 2nd tool "check_return_eligibility"

    We saw when we ran it that a rd tool was called taht we did not expect: "get_return_policy"
    We assume this was because the agent may have wanted the actual return-policy text so it could explain the eligibility decision to the customer.
    Due to the agent's interpretation of the prompt.
    """
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="Can I return order 12345?",
    )

    tool_call_details = get_tool_call_details(response)

    print("\nTOOL CALLS:")
    print(tool_call_details)

    assert tool_call_details[0] == {
        "name": "get_order_information",
        "args": {
            "order_id": "12345",
        },
    }

    assert tool_call_details[1] == {
        "name": "check_return_eligibility",
        "args": {
            "product_name": "Example Product",
            "days_since_purchase": 20,
            "opened": True,
            "defective": True,
        },
    }


@pytest.mark.llm
def test_agent_gets_product_name_from_order():
    """
    This test is more deterministic in expecting only 1 tool to be called,
    due to the way the prompt is written.
    """
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What is the product name for order 12345?",
    )

    tool_call_details = get_tool_call_details(response)

    print("\nTOOL CALLS:")
    print(tool_call_details)

    assert tool_call_details[0] == {
        "name": "get_order_information",
        "args": {
            "order_id": "12345",
        },
    }


@pytest.mark.llm
def test_agent_correctly_handles_return_eligibility_result():
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="Can I return order 12345?",
    )

    tool_results = get_tool_result_details(response)

    # print("\nTOOL RESULTS:")
    # print(tool_results)
    #
    # print("\nFINAL RESPONSE:")
    # print(response.text)

    eligibility_result = tool_results[1]["response"]

    assert eligibility_result["result"]["result"]["eligible"] is False

    assert "49.99" not in response.text

    assert "not eligible" in response.text.lower()
    assert "20 days" in response.text.lower()
    assert "14 days" in response.text.lower()



@pytest.mark.llm
def test_agent_updates_order_status():
    from src.tools import orders

    orders["12345"]["status"] = "Open"

    client = create_client()

    try:
        response = answer_customer_with_trace(
            client=client,
            question="Mark order 12345 as Reviewed.",
        )

        tool_call_details = get_tool_call_details(response)

        print("\nTOOL CALLS:")
        print(tool_call_details)

        print("\nFINAL RESPONSE:")
        print(response.text)

        assert any(
            call["name"] == "update_order_status"
            and call["args"] == {
                "order_id": "12345",
                "status": "Reviewed",
            }
            for call in tool_call_details
        )

        assert orders["12345"]["status"] == "Reviewed"

        assert "updated" in response.text.lower()
        assert "reviewed" in response.text.lower()

    finally:
        orders["12345"]["status"] = "Open"



@pytest.mark.llm
def test_agent_recovers_and_continues_after_order_lookup_failure():

    """
    Checks that the agent successfully did all three things"
    1. Recovered from the failure
    It didn't stop after get_order_information() failed.
    2. Used the recovery result
    It got the order information from search_order_database().
    3. Continued the workflow
    It used that information to construct the arguments for check_return_eligibility().
    This is a genuinely multi-step recovery workflow:
    """
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="Can I return order 54321?",
    )

    tool_call_details = get_tool_call_details(response)

    print("\nTOOL CALLS:")
    print(tool_call_details)

    assert tool_call_details[0] == {
        "name": "get_order_information",
        "args": {
            "order_id": "54321",
        },
    }

    assert tool_call_details[1] == {
        "name": "search_order_database",
        "args": {
            "order_id": "54321",
        },
    }

    assert tool_call_details[2] == {
        "name": "check_return_eligibility",
        "args": {
            "product_name": "Example Product",
            "days_since_purchase": 10,
            "opened": True,
            "defective": True,
        },
    }

    assert "eligible" in response.text.lower() or "return" in response.text.lower()


@pytest.mark.llm
def test_agent_uses_ticket_result_to_get_repository():
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What programming language is the repository for BUG-123 written in?",
    )

    # print("\nFINAL RESPONSE:")
    # print(response.text)

    tool_call_details = get_tool_call_details(response)

    print("\nTOOL CALLS:")
    print(tool_call_details)

    assert tool_call_details[0] == {
        "name": "get_ticket",
        "args": {
            "ticket_id": "BUG-123",
        },
    }

    assert tool_call_details[1] == {
        "name": "get_repository",
        "args": {
            "repository_name": "demo-app",
        },
    }

    assert "python" in response.text.lower()