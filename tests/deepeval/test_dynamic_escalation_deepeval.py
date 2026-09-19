import os
import pytest
from dotenv import load_dotenv

from deepeval import assert_test
from deepeval.dataset import EvaluationDataset, Golden
from deepeval.evaluate import AsyncConfig
from deepeval.metrics import (
    TaskCompletionMetric,
    StepEfficiencyMetric,
)
from deepeval.models import GeminiModel

from src.agent import answer_customer
from src.llm_client import create_client


@pytest.mark.llm
def test_dynamic_escalation_agent():
    load_dotenv()

    client = create_client()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY was not found.")

    judge_model = GeminiModel(
        model="gemini-3.5-flash-lite",
        api_key=api_key,
        temperature=0,
    )

    golden = Golden(
        input=(
            "Review the login implementation in demo-app_fail. "
            "Determine whether the implementation satisfies the repository's "
            "expected behavior. Source inspection alone is not sufficient; "
            "validate your conclusion using the repository's verification mechanism."
        ),
        expected_output=(
            "The login implementation does not satisfy the repository's "
            "expected behavior, and verification confirms the problem."
        ),
    )

    dataset = EvaluationDataset(
        goldens=[golden]
    )

    metrics = [
        TaskCompletionMetric(
            threshold=0.8,
            model=judge_model,
        ),
        StepEfficiencyMetric(
            threshold=0.8,
            model=judge_model,
        ),
    ]

    for golden in dataset.evals_iterator(
        metrics=metrics,
        async_config=AsyncConfig(run_async=False),
    ):
        answer_customer(
            client=client,
            question=golden.input,
        )

        assert_test(
            golden=golden,
            metrics=metrics,
        )