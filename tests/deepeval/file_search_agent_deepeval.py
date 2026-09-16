
from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.metrics import TaskCompletionMetric, StepEfficiencyMetric

from src.agent import answer_customer_with_trace
from src.llm_client import create_client

from tests.deepeval.helpers import create_gemini_model

gemini_model = create_gemini_model()


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
    print(response.final_text)

    assert "src/login.py" in response.final_text.lower()

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