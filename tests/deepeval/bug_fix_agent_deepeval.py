import os

from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.metrics import TaskCompletionMetric, StepEfficiencyMetric
from deepeval.models import GeminiModel

from src.agent import answer_customer_with_trace
from src.llm_client import create_client
from src.tools import bug_fixed


gemini_model = GeminiModel(
    model="gemini-2.5-flash",
    api_key=os.environ["GEMINI_API_KEY"],
    temperature=0,
)


TASK = (
    "Investigate BUG-456, fix the failing test, "
    "and verify that the tests pass."
)


def test_bug_fix_agent_trajectory():
    bug_fixed["BUG-456"] = False

    golden = Golden(input=TASK)

    try:
        response = answer_customer_with_trace(
            client=create_client(),
            question=golden.input,
        )

        print("\nFINAL RESPONSE:")
        print(response.text)

        assert bug_fixed["BUG-456"] is True
        assert "pass" in response.text.lower()

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
        bug_fixed["BUG-456"] = False