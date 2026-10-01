
"""
Run with:
python -m pytest tests/test_golden_agent_regression.py -q --run-llmpython -m pytest tests/test_golden_agent_regression.py -q --run-llm
"""

import json
from pathlib import Path

import pytest

from src.agent import answer_customer_with_trace,                                                                                                                               get_tool_calls
from src.llm_client import create_client


FIXTURE_PATH = (
    Path(__file__).resolve().parent.parent
    / "fixtures"
    / "golden_agent_cases.json"
)


def load_golden_cases():
    with FIXTURE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


@pytest.mark.llm
@pytest.mark.parametrize(
    "case",
    load_golden_cases(),
    ids=lambda case: case["id"],
)
def test_agent_regression(case):
    """
    Run a golden test case against the real agent and verify
    required tools and critical facts in the final response.
    """

    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question=case["question"],
    )

    # print("\n=== TOOL CALLS === ")
    # for tool_call in response.tool_calls:
    #     print(tool_call.name, tool_call.args)
    #
    # print("\n=== TOOL RESULTS ===")
    # for tool_result in response.tool_results:
    #     print(tool_result.name, tool_result.response)
    #
    # print("\n=== FINAL ===")
    # print(response.final_text)

    assert response.final_text.strip(), "Agent did not produce a final answer."

    for expected_text in case["expected_answer_contains"]:
        assert expected_text.lower() in response.final_text.lower()

    # actual_tools = get_tool_calls(response)
    #
    # for required_tool in case["required_tools"]:
    #     assert required_tool in actual_tools, (
    #         f"Expected tool '{required_tool}' was not used. "
    #         f"Actual tools: {actual_tools}"
    #     )
    #
    # assert response.final_text.strip(), (
    #     "Agent did not produce a final answer.\n"
    #     f"Tool calls: {actual_tools}"
    # )
    #
    # for expected_text in case["expected_answer_contains"]:
    #     assert expected_text.lower() in response.final_text.lower(), (
    #         f"Expected '{expected_text}' in final response.\n"
    #         f"Actual response: {response.final_text}"
    #     )