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


TASK = "What programming language is the repository for BUG-123 written in?"


def test_coding_agent_trajectory():
    """
    Testing that the agent actually answered the user's question - the answer is python.
    And that the steps taken were efficient.
    Run with: deepeval test run tests/deepeval/coding_agent_trajectory_deepeval.py
    """
    golden = Golden(input=TASK)

    response = answer_customer_with_trace(
        client=create_client(),
        question=golden.input,
    )

    print("\nFINAL RESPONSE:")
    print(response.text)

    assert "python" in response.text.lower()

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