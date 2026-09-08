import os

from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.metrics import TaskCompletionMetric, StepEfficiencyMetric
from deepeval.models import GeminiModel

from src.agent import answer_customer_with_trace
from src.llm_client import create_client


gemini_model = GeminiModel(
    model="gemini-2.5-flash",
    api_key=os.environ["GEMINI_API_KEY"],
    temperature=0,
)

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