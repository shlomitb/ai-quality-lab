
from dotenv import load_dotenv

from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from src.agent import answer_customer
from src.llm_client import create_client

from tests.deepeval.helpers import create_gemini_model

load_dotenv()

gemini_model = create_gemini_model()

client = create_client()


golden = Golden(
    input="Can I return an unopened physical product after 20 days?"
)


correctness_metric = GEval(
    name="Return Policy Correctness",
    model=gemini_model,
    criteria=(
        "The AI should clearly state that an unopened physical product "
        "purchased 20 days ago can be returned because unopened products "
        "can be returned within 30 days."
    ),
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
    ],

    threshold=0.5,
)


def return_policy_agent():

    actual_output = answer_customer(
        client=client,
        question=golden.input,
    )

    test_case = LLMTestCase(
        input=golden.input,
        actual_output=actual_output,
    )

    assert_test(
        test_case=test_case,
        metrics=[correctness_metric],
    )