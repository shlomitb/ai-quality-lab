
from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.metrics import TaskCompletionMetric, StepEfficiencyMetric

from src.agent import answer_customer_with_trace
from src.llm_client import create_client

from tests.deepeval.helpers import create_gemini_model

gemini_model = create_gemini_model()


TASK = "What is the price of the Unavailable Product?"


def test_recovery_trajectory():
    golden = Golden(input=TASK)

    answer_customer_with_trace(
        client=create_client(),
        question=golden.input,
    )

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


