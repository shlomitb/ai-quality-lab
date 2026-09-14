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


TASK = "Investigate BUG-123 and find the file related to the login problem."


def test_file_search_agent_trajectory():
    """
    Task Completion metric:
    The agent accomplished the actual task: it investigated the ticket, identified the repository, found the relevant file, and reported it.

    Step Efficiency metric:
    The agent used the shortest sensible path: get_ticket → search_files
    """
    golden = Golden(input=TASK)

    response = answer_customer_with_trace(
        client=create_client(),
        question=golden.input,
    )

    print("\nFINAL RESPONSE:")
    print(response.text)

    assert "src/login.py" in response.text.lower()

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