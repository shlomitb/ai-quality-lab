
from pathlib import Path

from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.metrics import TaskCompletionMetric, StepEfficiencyMetric

from src.agent import answer_customer_with_trace
from src.llm_client import create_client

from tests.deepeval.helpers import create_gemini_model

#deepeval test run tests/deepeval/bug_fix_real_code_deepeval.py

gemini_model = create_gemini_model()


TASK = (
    "Investigate BUG-456, fix the failing test, "
    "and verify that the tests pass."
)


def test_real_code_bug_fix_trajectory():
    file_path = Path("demo_repo/src/login.py")

    broken_content = """def login(username, password):
        if username and password:
            return False
        return False
    """

    file_path.write_text(broken_content)

    golden = Golden(input=TASK)

    try:
        response = answer_customer_with_trace(
            client=create_client(),
            question=golden.input,
        )

        print("\nFINAL RESPONSE:")
        print(response.text)

        # Direct verification of the real file state.
        assert file_path.read_text() != broken_content

        # Direct verification of the final test result.
        from src.tools import run_tests

        post_test_result = run_tests("demo-app_fail")

        print("\nPOST TEST RESULT:")
        print(post_test_result)

        assert post_test_result["result"]["status"] == "passed"

        task_completion = TaskCompletionMetric(
            threshold=0.5,
            model=gemini_model,
            task=TASK,
        )

        step_efficiency = StepEfficiencyMetric(
            threshold=0.5,
            model=gemini_model,
        )

        assert_test(
            golden=golden,
            metrics=[task_completion, step_efficiency],
        )

    finally:
        file_path.write_text(broken_content)