from src.llm_client import create_client
from src.agent import answer_customer_with_trace, get_tool_calls

import pytest


"""
There are 2 tools in answer_customer_with_trace
and here we test that the llm choosed the correct tool to use based on the question asked.add
"""


@pytest.mark.llm
def test_agent_calls_return_policy_tool():
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
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question="What is the price of the Example Product?"
    )

    tool_calls = get_tool_calls(response)

    assert tool_calls == ["get_product_information"]