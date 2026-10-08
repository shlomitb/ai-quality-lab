"""
DeepEval evaluation of a task requiring dynamic tool access.

Evaluates whether the agent completes the task successfully and uses
an efficient trajectory while handling the need for additional tool access.

Direct permission and dynamic-access enforcement are tested separately.
"""

import os

import pytest
from dotenv import load_dotenv

from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.metrics import (
    TaskCompletionMetric,
    StepEfficiencyMetric,
)
from deepeval.models import GeminiModel

from src.agent import answer_customer_with_trace


# Save DeepEval test runs in our project reports directory.
os.environ.setdefault(
    "DEEPEVAL_RESULTS_FOLDER",
    "./reports/deepeval",
)


@pytest.mark.llm
def test_dynamic_tool_access_task_completion(llm_client):
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

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY was not found.")

    judge_model = GeminiModel(
        model="gemini-3.5-flash-lite",
        api_key=api_key,
        temperature=0,
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

    response = answer_customer_with_trace(
        client=llm_client,
        question=golden.input,
    )

    print("\nAGENT TOOL CALLS:")
    print(response.tool_calls)

    print("\nFINAL RESPONSE:")
    print(response.final_text)

    assert_test(
        golden=golden,
        metrics=metrics,
    )