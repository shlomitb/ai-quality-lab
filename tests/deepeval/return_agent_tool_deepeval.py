
import os

from dotenv import load_dotenv

from deepeval import assert_test
from deepeval.metrics import ToolCorrectnessMetric
from deepeval.models import GeminiModel
from deepeval.test_case import LLMTestCase, ToolCall

from src.agent import answer_customer_with_trace, get_tool_calls
from src.llm_client import create_client

load_dotenv()


"""
This test checks similar to the test_agent_trace_with_mock,
Just here it does it with an LLM call and there not

It is enough for this test case to use the Mock one, 
We should not "use DeepEval because it's available," but "use DeepEval when it provides something our deterministic test cannot reliably provide."
"""


gemini_model = GeminiModel(
    model="gemini-2.5-flash",
    api_key=os.environ["GEMINI_API_KEY"],
    temperature=0,
)

metric = ToolCorrectnessMetric(
    threshold=0.5,
    model=gemini_model,
)



def test_return_policy_tool_correctness():
    client = create_client()

    question = "Can I return an opened product after 20 days if defective?"

    response = answer_customer_with_trace(
        client=client,
        question=question,
    )

    tool_names = get_tool_calls(response)

    actual_tools = [
        ToolCall(name=name)
        for name in tool_names
    ]

    expected_tools = [
        ToolCall(name="get_return_policy")  #"some_other_tool" - used this to see it fail as a one off
    ]

    test_case = LLMTestCase(
        input=question,
        actual_output=response.text,
        tools_called=actual_tools,
        expected_tools=expected_tools,
    )

    metric = ToolCorrectnessMetric(
        threshold=0.5,
        model=gemini_model,
    )

    assert_test(
        test_case=test_case,
        metrics=[metric],
    )