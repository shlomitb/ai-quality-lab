from src.llm_client import create_client
from src.agent import answer_customer_with_trace, get_tool_calls

import pytest


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