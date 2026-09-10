import os

from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.metrics import StepEfficiencyMetric
from deepeval.models import GeminiModel
from deepeval.tracing import observe, update_current_trace

from src.tools import get_return_policy, get_product_information


gemini_model = GeminiModel(
    model="gemini-2.5-flash",
    api_key=os.environ["GEMINI_API_KEY"],
    temperature=0,
)


TASK = (
    "Can I return the Example Product after 20 days, "
    "and what is its price?"
)


@observe(type="agent")
def efficient_agent():
    get_return_policy()
    get_product_information("Example Product")

    output = (
        "The Example Product costs $49.99. "
        "Unopened products can be returned within 30 days. "
        "Opened products can be returned within 14 days if defective."
    )

    update_current_trace(
        input=TASK,
        output=output,
    )

    return output


@observe(type="agent")
def inefficient_agent():
    get_return_policy()
    get_product_information("Example Product")
    get_return_policy()

    output = (
        "The Example Product costs $49.99. "
        "Unopened products can be returned within 30 days. "
        "Opened products can be returned within 14 days if defective."
    )

    update_current_trace(
        input=TASK,
        output=output,
    )

    return output


def test_efficient_agent():
    golden = Golden(input=TASK)

    efficient_agent()

    metric = StepEfficiencyMetric(
        threshold=0.5,
        model=gemini_model,
    )

    assert_test(
        golden=golden,
        metrics=[metric],
    )


def test_inefficient_agent():
    golden = Golden(input=TASK)

    inefficient_agent()

    metric = StepEfficiencyMetric(
        threshold=0.5,
        model=gemini_model,
    )

    assert_test(
        golden=golden,
        metrics=[metric],
    )