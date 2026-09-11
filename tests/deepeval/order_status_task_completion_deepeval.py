import os

from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.metrics import TaskCompletionMetric
from deepeval.models import GeminiModel

from src.agent import answer_customer_with_trace
from src.llm_client import create_client
from src.tools import orders


gemini_model = GeminiModel(
    model="gemini-2.5-flash",
    api_key=os.environ["GEMINI_API_KEY"],
    temperature=0,
)


TASK = "Mark order 12345 as Reviewed."


def test_order_status_task_completion():

    """
    This test is not checking the value: orders["12345"]["status"] == "Reviewed"
    The deterministic test does that.
    Here we are checking if the agent's overall trajectory accomplish the task:
    Using TaskCompletionMetric
    This test has an LLM client and a judge call

    run with:
    deepeval test run tests/deepeval/order_status_task_completion_deepeval.py

    Result: The system successfully invoked the 'update_order_status' tool with the correct order ID and
    status, and the tool confirmed the order was updated to 'Reviewed', perfectly matching the desired task.
    """
    # Start from a known state
    orders["12345"]["status"] = "Open"

    golden = Golden(input=TASK)

    answer_customer_with_trace(
        client=create_client(),
        question=golden.input,
    )

    metric = TaskCompletionMetric(
        threshold=0.5,
        model=gemini_model,
        task=TASK,
    )

    try:
        assert_test(
            golden=golden,
            metrics=[metric],
        )
    finally:
        # Reset shared state for other tests
        orders["12345"]["status"] = "Open"