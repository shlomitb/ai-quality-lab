
from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.metrics import TaskCompletionMetric, StepEfficiencyMetric

from src.agent import answer_customer_with_trace
from src.llm_client import create_client
from tests.deepeval.helpers import create_gemini_model


gemini_model = create_gemini_model()

task_completion = TaskCompletionMetric(
    threshold=0.5,
    model=gemini_model,
)

step_efficiency = StepEfficiencyMetric(
    threshold=0.5,
    model=gemini_model,
)


def test_return_agent_trajectory():
    golden = Golden(
        input=(
            "Can I return the Example Product after 20 days, "
            "" "and what is its price?")
    )

    answer_customer_with_trace(
        client=create_client(),
        question=golden.input,
    )

    assert_test(
        golden=golden,
        metrics=[task_completion, step_efficiency],
    )