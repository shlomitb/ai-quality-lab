"""
DeepEval tests for real code-change workflows.

These tests exercise the agent against actual files in demo_repo,
including making a code change and verifying the resulting test state.
"""

from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.metrics import TaskCompletionMetric, StepEfficiencyMetric

from src.agent import answer_customer_with_trace
from src.tools import run_tests
from tests.deepeval.helpers import create_gemini_model

gemini_model = create_gemini_model()


def test_real_code_bug_fix_trajectory(llm_client, restore_login_file):
    """
    tests the agent against an actual file rather than your bug_fixed mock state.
    Has deterministic checks, asserts
    And has DeepEval metric test
    It is a real-world integration test, not primarily an LLM evaluation test.
    """

    task = (
        "Investigate BUG-456, fix the failing test, "
        "and verify that the tests pass."
    )

    file_path = restore_login_file

    broken_content = """def login(username, password):
        if username and password:
            return False
        return False
    """

    file_path.write_text(broken_content)

    golden = Golden(input=task)

    response = answer_customer_with_trace(
        client=llm_client,
        question=golden.input,
    )

    print("\nFINAL RESPONSE:")
    print(response.final_text)

    # Direct verification of the real file state.
    assert file_path.read_text() != broken_content

    post_test_result = run_tests("demo-app_fail")

    print("\nPOST TEST RESULT:")
    print(post_test_result)

    assert post_test_result["result"]["status"] == "passed"

    task_completion = TaskCompletionMetric(
        threshold=0.5,
        model=gemini_model,
        task=task,
    )

    step_efficiency = StepEfficiencyMetric(
        threshold=0.5,
        model=gemini_model,
    )

    assert_test(
        golden=golden,
        metrics=[task_completion, step_efficiency],
    )