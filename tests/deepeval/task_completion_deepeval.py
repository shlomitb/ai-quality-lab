

from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.metrics import TaskCompletionMetric

from src.agent import answer_customer_with_trace
from src.llm_client import create_client
from src.tools import orders, bug_fixed

from tests.deepeval.helpers import create_gemini_model



"""
DeepEval Task Completion tests.

These tests evaluate whether the agent accomplished the requested task.
Deterministic assertions are used where the expected state or answer can
be verified directly; TaskCompletionMetric evaluates the agent's overall
task completion.
"""

gemini_model = create_gemini_model()



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

    task = "Mark order 12345 as Reviewed."
    orders["12345"]["status"] = "Open"

    golden = Golden(input=task)

    answer_customer_with_trace(
        client=create_client(),
        question=golden.input,
    )

    metric = TaskCompletionMetric(
        threshold=0.5,
        model=gemini_model,
        task=task,
    )

    try:
        assert_test(
            golden=golden,
            metrics=[metric],
        )
    finally:
        # Reset shared state for other tests
        orders["12345"]["status"] = "Open"



def test_bug_file_search_task_completion():
    """
    Task Completion metric:
    The agent accomplished the actual task: it investigated the ticket, identified the repository, found the relevant file, and reported it.
    """
    task = "Investigate BUG-123 and find the file related to the login problem."

    golden = Golden(input=task)

    response = answer_customer_with_trace(
        client=create_client(),
        question=golden.input,
    )

    print("\nFINAL RESPONSE:")
    print(response.final_text)

    assert "src/login.py" in response.final_text.lower()

    task_completion = TaskCompletionMetric(
        threshold=0.5,
        model=gemini_model,
        task=task,
    )

    assert_test(
        golden=golden,
        metrics=[task_completion],
    )


def test_bug_fix_agent_task_completion():
    task = (
        "Investigate BUG-456, fix the failing test, "
        "and verify that the tests pass."
    )
    bug_fixed["BUG-456"] = False

    golden = Golden(input=task)

    try:
        response = answer_customer_with_trace(
            client=create_client(),
            question=golden.input,
        )

        print("\nFINAL RESPONSE:")
        print(response.final_text)

        assert bug_fixed["BUG-456"] is True
        assert "pass" in response.final_text.lower()

        task_completion = TaskCompletionMetric(
            threshold=0.5,
            model=gemini_model,
            task=task,
        )

        assert_test(
            golden=golden,
            metrics=[task_completion],
        )

    finally:
        bug_fixed["BUG-456"] = False




def test_return_eligibility_task_completion():
    task = "Can I return order 54321?"
    golden = Golden(input=task)

    answer_customer_with_trace(
        client=create_client(),
        question=golden.input,
    )

    task_completion = TaskCompletionMetric(
        threshold=0.5,
        model=gemini_model,
        task=task,
    )

    assert_test(
        golden=golden,
        metrics=[task_completion],
    )


def test_unavailable_product_task_completion():
    task = "What is the price of the Unavailable Product?"
    golden = Golden(input=task)

    answer_customer_with_trace(
        client=create_client(),
        question=golden.input,
    )

    task_completion = TaskCompletionMetric(
        threshold=0.5,
        model=gemini_model,
        task=task,
    )

    assert_test(
        golden=golden,
        metrics=[task_completion],
    )


def test_bug_repository_language_task_completion():
    """
    Testing that the agent actually answered the user's question - the answer is python.
    And that the steps taken were efficient.
    Run with: deepeval test run tests/deepeval/coding_agent_trajectory_deepeval.py
    """

    task = "What programming language is the repository for BUG-123 written in?"

    golden = Golden(input=task)

    response = answer_customer_with_trace(
        client=create_client(),
        question=golden.input,
    )

    print("\nFINAL RESPONSE:")
    print(response.final_text)

    assert "python" in response.final_text.lower()

    task_completion = TaskCompletionMetric(
        threshold=0.5,
        model=gemini_model,
        task=task,
    )

    assert_test(
        golden=golden,
        metrics=[task_completion],
    )


