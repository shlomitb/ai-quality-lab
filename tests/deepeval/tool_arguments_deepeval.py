"""
DeepEval Tool Argument Correctness tests.

These tests evaluate whether the arguments supplied to a selected tool
are appropriate for the user's request.

This is different from tool selection:

    Tool selection:
        Did the agent choose the correct tool?

    Tool arguments:
        Given that tool, did the agent provide the correct arguments?

The agent itself makes the first LLM call. DeepEval then uses an LLM
judge to evaluate whether the observed tool arguments were correct.

To run:
deepeval test run .\tests\deepeval\tool_arguments_deepeval.py -k test_product_information_tool_argument_correctness -v -s --run-llm
"""
import pytest
from deepeval import assert_test
from deepeval.metrics import ArgumentCorrectnessMetric
from deepeval.test_case import LLMTestCase, ToolCall

from src.agent import answer_customer_with_trace, get_tool_call_details
from tests.deepeval.helpers import create_gemini_model



gemini_model = create_gemini_model()


@pytest.mark.llm
def test_product_information_tool_argument_correctness(llm_client):
    """
    Gemini LLM call #1
    → runs your agent
    → chooses tool + argument

    Gemini LLM call #2
    → DeepEval ArgumentCorrectnessMetric
    → judges whether the argument was correct

    Given the user's request, does the argument the agent generated make sense?
    """

    question = "What is the price of the Example Product?"

    response = answer_customer_with_trace(
        client=llm_client,
        question=question,
    )

    tool_call_details = get_tool_call_details(response)

    tools_called = [
        ToolCall(
            name=tool["name"],
            input_parameters=tool["args"],
        )
        for tool in tool_call_details
    ]

    test_case = LLMTestCase(
        input=question,
        actual_output=response.final_text,
        tools_called=tools_called,
    )

    metric = ArgumentCorrectnessMetric(
        threshold=0.5,
        model=gemini_model,
    )

    assert_test(
        test_case=test_case,
        metrics=[metric],
    )