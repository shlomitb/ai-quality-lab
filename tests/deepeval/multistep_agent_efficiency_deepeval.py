
from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.metrics import StepEfficiencyMetric

from src.agent import answer_customer_with_trace
from src.llm_client import create_client

from tests.deepeval.helpers import create_gemini_model

gemini_model = create_gemini_model()


TASK = "Can I return order 12345?"


def test_multistep_agent_step_efficiency():
    """
    The first time this ran, it failed since it returned 2 tools:
    'check_return_eligibility' and get_return_policy' (an unnecessary  action for the strict determination of eligibility)

    Then we updated the agent's instructions to be more specific:
    In: answer_customer_with_trace() added:
        "Use get_return_policy only when the customer asks for
        the return policy or when the available order/eligibility
        information is insufficient to answer the question.

        Do not call get_return_policy solely to explain an
        eligibility result that has already been determined."

    That did not help so refined the return message in the tool check_return_eligibility to be:
    "reason": (
        "Opened defective products can only be returned within "
        "14 days. This order is 20 days old."
    ),
    """
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