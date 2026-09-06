from src.llm_client import create_client
from src.agent import answer_customer_with_trace, get_tool_calls, get_tool_call_details

import pytest


"""
There are 2 tools in answer_customer_with_trace
and here we test that the llm chose the correct tool to use based on the question asked.py

A real LLM integration test with deterministic assertions.

→ Gemini actually runs the agent
→ the real agent makes the tool-selection/argument decision
Then:
Deterministic assertion
→ we check the result against an exact expected value
"""


@pytest.mark.llm
def test_agent_calls_return_policy_tool():
    """
        There are 2 tools in answer_customer_with_trace
        Here test that the tool called is "get_return_policy"
       :return:
    """
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
    """
        There are 2 tools in answer_customer_with_trace
        Here test that the tool called is "get_product_information"
    :return:
    """
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What is the price of the Example Product?"
    )

    tool_calls = get_tool_calls(response)

    assert tool_calls == ["get_product_information"]


@pytest.mark.llm
def test_agent_passes_correct_product_name():
    """
    test that the product name is returned as an argument in the llm response
    :return:
    """
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