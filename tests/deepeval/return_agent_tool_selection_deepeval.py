import os

from dotenv import load_dotenv
from deepeval import assert_test
from deepeval.metrics import ToolCorrectnessMetric
from deepeval.models import GeminiModel
from deepeval.test_case import LLMTestCase, ToolCall

from src.agent import answer_customer_with_trace, get_tool_calls
from src.llm_client import create_client


load_dotenv()

gemini_model = GeminiModel(
    model="gemini-2.5-flash",
    api_key=os.environ["GEMINI_API_KEY"],
    temperature=0,
)


def test_return_policy_tool_selection():
    client = create_client()

    question = "Can I return an unopened physical product after 20 days?"

    response = answer_customer_with_trace(
        client=client,
        question=question,
    )

    tool_names = get_tool_calls(response)

    tools_called = [
        ToolCall(name=name)
        for name in tool_names
    ]

    expected_tools = [
        ToolCall(name="get_return_policy")
    ]

    available_tools = [
        ToolCall(name="get_return_policy"),
        ToolCall(name="get_product_information")
    ]

    test_case = LLMTestCase(
        input=question,
        actual_output=response.text,
        tools_called=tools_called,
        expected_tools=expected_tools,
    )

    metric = ToolCorrectnessMetric(
        threshold=0.5,
        model=gemini_model,
        available_tools=available_tools,
    )

    assert_test(
        test_case=test_case,
        metrics=[metric],
    )

def test_product_info_tool_selection():
    client = create_client()

    question = "What is the price of the Example Product?"

    response = answer_customer_with_trace(
        client=client,
        question=question,
    )

    tool_names = get_tool_calls(response)

    tools_called = [
        ToolCall(name=name)
        for name in tool_names
    ]

    expected_tools = [
        ToolCall(name="get_product_information")
    ]

    available_tools = [
        ToolCall(name="get_return_policy"),
        ToolCall(name="get_product_information")
    ]

    test_case = LLMTestCase(
        input=question,
        actual_output=response.text,
        tools_called=tools_called,
        expected_tools=expected_tools,
    )

    metric = ToolCorrectnessMetric(
        threshold=0.5,
        model=gemini_model,
        available_tools=available_tools,
    )

    assert_test(
        test_case=test_case,
        metrics=[metric],
    )