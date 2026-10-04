"""
DeepEval Task Completion tests.

These tests evaluate whether the agent accomplished the requested task.
Deterministic assertions are used where the expected state or answer can
be verified directly; TaskCompletionMetric evaluates the agent's overall
task completion.

Run tests here with:
deepeval test run tests\deepeval\task_completion_deepeval.py -k test_bug_file_search_task_completion
"""
import pytest
from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.metrics import TaskCompletionMetric

from src.agent import answer_customer_with_trace
from src.llm_client import create_client
from src.tools import orders, bug_fixed
from tests.deepeval.helpers import create_gemini_model


gemini_model = create_gemini_model()



def test_bug_file_search_task_completion():
    """
    Task Completion metric:
    The agent accomplished the actual task: it investigated the ticket, identified the repository, found the relevant file, and reported it.
    """

    task = (
        "Investigate BUG-123 and identify the source file related to the "
        "login problem. Do not modify any files or run tests."
    )

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


def test_bug_fix_agent_task_completion(restore_login_file):
    task = (
        "Investigate BUG-456, fix the failing test, "
        "and verify that the tests pass."
    )

    # Ensure the test always starts with the known broken implementation.
    broken_login = """def login(username, password):
        if username == "alice" and password == "password":
            return False
        return False
    """

    restore_login_file.write_text(
        broken_login,
        encoding="utf-8",
    )

    golden = Golden(input=task)

    response = answer_customer_with_trace(
        client=create_client(),
        question=golden.input,
    )

    print("\nAGENT TOOL CALLS:")
    print(response.tool_calls)

    print("\nTOOL RESULTS:")
    print(response.tool_results)

    print("\nFINAL RESPONSE:")
    print(response.final_text)

    tool_names = [tool.name for tool in response.tool_calls]

    assert "edit_file" in tool_names
    assert tool_names.count("run_tests") >= 2
    assert response.final_text.strip()

    task_completion = TaskCompletionMetric(
        threshold=0.5,
        model=gemini_model,
        task=task,
    )

    assert_test(
        golden=golden,
        metrics=[task_completion],
    )


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




@pytest.mark.llm
def test_agent_does_not_claim_success_when_verification_fails(
    restore_login_file,
):
    """
    The agent must accurately report a failed verification result.

    The repository intentionally starts with a failing login test.
    The agent is asked to investigate and verify the problem without
    modifying the source code.
    """

    task = (
        "Investigate BUG-456 in demo-app_fail and verify whether the "
        "login problem is currently fixed. Do not modify any files. "
        "Run the repository tests and accurately report whether they pass."
    )

    golden = Golden(input=task)

    response = answer_customer_with_trace(
        client=create_client(),
        question=golden.input,
    )

    print("\nAGENT TOOL CALLS:")
    print(response.tool_calls)

    print("\nTOOL RESULTS:")
    print(response.tool_results)

    print("\nFINAL RESPONSE:")
    print(response.final_text)

    task_completion = TaskCompletionMetric(
        threshold=0.5,
        model=gemini_model,
        task=task,
    )

    assert_test(
        golden=golden,
        metrics=[task_completion],
    )



# ---------------------------------------------------------------------------
# Temporarily disabled: order-management Task Completion test
#
# This test was written before the agent was changed to use skill-based
# tool authorization. The order-management tools still exist in tools.py
# (get_order_information, update_order_status, search_order_database), but
# no current skill authorizes these tools.
#
# As a result, the agent cannot legitimately complete:
#     "Mark order 12345 as Reviewed."
#
# Without access to the appropriate tools, the agent attempts to discover
# the order system using search_files, repeatedly guesses repository names,
# and eventually reaches MAX_AGENT_TURNS. This is a valid demonstration of
# an agent-recovery problem, but it is not a valid positive Task Completion
# evaluation in the current architecture.
#
# To restore this test as a positive Task Completion test, we would need to:
#   1. Create an appropriate order-management skill.
#   2. Define its initial_tools and/or requestable_tools in TOOL_ACCESS_POLICY.
#   3. Include the relevant order tools in that skill's tool configuration.
#   4. Add the corresponding skill documentation/prompt describing how to
#      investigate and update an order.
#   5. Update skill routing so this task selects the order-management skill.
#
# Once those pieces exist, this test can be re-enabled and should verify
# that the agent can retrieve order information, update the status to
# "Reviewed", and report successful completion.
# ---------------------------------------------------------------------------
# def test_order_status_task_completion():
#
#     """
#     This test is not checking the value: orders["12345"]["status"] == "Reviewed"
#     The deterministic test does that.
#     Here we are checking if the agent's overall trajectory accomplish the task:
#     Using TaskCompletionMetric
#     This test has an LLM client and a judge call
#
#     run with:
#     deepeval test run tests/deepeval/order_status_task_completion_deepeval.py
#
#     Result: The system successfully invoked the 'update_order_status' tool with the correct order ID and
#     status, and the tool confirmed the order was updated to 'Reviewed', perfectly matching the desired task.
#     """
#     # Start from a known state
#
#     task = "Mark order 12345 as Reviewed."
#     orders["12345"]["status"] = "Open"
#
#     golden = Golden(input=task)
#
#     answer_customer_with_trace(
#         client=create_client(),
#         question=golden.input,
#     )
#
#     metric = TaskCompletionMetric(
#         threshold=0.5,
#         model=gemini_model,
#         task=task,
#     )
#
#     try:
#         assert_test(
#             golden=golden,
#             metrics=[metric],
#         )
#     finally:
#         # Reset shared state for other tests
#         orders["12345"]["status"] = "Open"

