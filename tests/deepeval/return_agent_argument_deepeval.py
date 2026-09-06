import os

from dotenv import load_dotenv
from deepeval import assert_test
from deepeval.metrics import ArgumentCorrectnessMetric
from deepeval.models import GeminiModel
from deepeval.test_case import LLMTestCase, ToolCall

from src.agent import answer_customer_with_trace, get_tool_call_details
from src.llm_client import create_client


load_dotenv()

gemini_model = GeminiModel(
    model="gemini-2.5-flash",
    api_key=os.environ["GEMINI_API_KEY"],
    temperature=0,
)


def test_product_information_argument_correctness():
    """
    Gemini LLM call #1
    → runs your agent
    → chooses tool + argument

    Gemini LLM call #2
    → DeepEval ArgumentCorrectnessMetric
    → judges whether the argument was correct

    Given the user's request, does the argument the agent generated make sense?

    :return:
    """
    client = create_client()

    question = "What is the price of the Example Product?"

    response = answer_customer_with_trace(
        client=client,
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
        actual_output=response.text,
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