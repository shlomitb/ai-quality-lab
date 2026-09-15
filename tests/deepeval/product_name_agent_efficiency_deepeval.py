
from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.metrics import StepEfficiencyMetric

from src.agent import answer_customer_with_trace
from src.llm_client import create_client

from tests.deepeval.helpers import create_gemini_model

gemini_model = create_gemini_model()

TASK = "What is the product name for order 12345?"


def test_product_name_agent_step_efficiency():
    golden = Golden(input=TASK)

    answer_customer_with_trace(
        client=create_client(),
        question=golden.input,
    )

    metric = StepEfficiencyMetric(
        threshold=0.5,
        model=gemini_model,
    )

    assert_test(
        golden=golden,
        metrics=[metric],
    )