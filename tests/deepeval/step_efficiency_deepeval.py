"""
DeepEval Step Efficiency tests.

Evaluate whether the agent completes tasks without unnecessary steps.
These tests do not assert an exact tool sequence.

Exact tool selection is tested separately in tool_selection_deepeval.py.

Run with:
deepeval test run tests\deepeval\step_efficiency_deepeval.py -k test_bug_file_search_step_efficiency -v -s
"""

from deepeval import assert_test
from deepeval.dataset import Golden
from deepeval.metrics import StepEfficiencyMetric

from src.agent import answer_customer_with_trace

from tests.deepeval.helpers import create_gemini_model

gemini_model = create_gemini_model()


def test_bug_file_search_step_efficiency(llm_client):
    """
    Evaluate efficiency of a repository investigation task.

    The agent must investigate BUG-123 and find the file related to
    the login problem. Step Efficiency evaluates whether the agent
    avoids unnecessary investigation steps while following the
    skill's tool-authorization policy.
    """
    task = (
        "Investigate BUG-123 and find the file related to the login problem. "
        "This is a file-identification task only. Do not modify files or fix "
        "the bug; identify the relevant repository and source file."
    )
    golden = Golden(input=task)

    response = answer_customer_with_trace(
        client=llm_client,
        question=golden.input,
    )

    print("\nAGENT TOOL CALLS:")
    print(response.tool_calls)

    print("\nFINAL RESPONSE:")
    print(response.final_text)

    metric = StepEfficiencyMetric(
        threshold=0.5,
        model=gemini_model,
    )

    assert_test(
        golden=golden,
        metrics=[metric],
    )


def test_login_verification_step_efficiency():
    """
    Evaluate efficiency of a multi-step repository verification task.

    The agent must inspect the login implementation and validate its
    conclusion using the repository's verification mechanism.
    Step Efficiency evaluates whether it avoids unnecessary actions.
    """
    task = (
        "Review the login implementation in demo-app_fail. "
        "Determine whether the implementation satisfies the repository's "
        "expected behavior. Source inspection alone is not sufficient; "
        "validate your conclusion using the repository's verification mechanism."
    )
    golden = Golden(input=task)

    response = answer_customer_with_trace(
        client=create_client(),
        question=golden.input,
    )

    print("\nAGENT TOOL CALLS:")
    print(response.tool_calls)

    print("\nFINAL RESPONSE:")
    print(response.final_text)

    metric = StepEfficiencyMetric(
        threshold=0.5,
        model=gemini_model,
    )

    assert_test(
        golden=golden,
        metrics=[metric],
    )

# def test_product_name_step_efficiency():
#     """
#     Evaluate the efficiency of a simple product-information task.
#
#     The agent should be able to answer the question without unnecessary
#     tool calls.
#     """
#     task = "What is the product name for order 12345?"
#     golden = Golden(input=task)
#
#     response = answer_customer_with_trace(
#         client=create_client(),
#         question=golden.input,
#     )
#
#     print("\nAGENT TOOL CALLS:")
#     print(response.tool_calls)
#
#     print("\nFINAL RESPONSE:")
#     print(response.final_text)
#
#     metric = StepEfficiencyMetric(
#         threshold=0.5,
#         model=gemini_model,
#     )
#
#     assert_test(
#         golden=golden,
#         metrics=[metric],
#     )
#
#
# def test_return_eligibility_step_efficiency():
#     """
#     Evaluate efficiency when determining return eligibility.
#
#     This scenario is useful because the agent may be able to answer
#     from the eligibility information alone, without an additional
#     get_return_policy call.
#     """
#     task = "Can I return order 12345?"
#     golden = Golden(input=task)
#
#     response = answer_customer_with_trace(
#         client=create_client(),
#         question=golden.input,
#     )
#
#     print("\nAGENT TOOL CALLS:")
#     print(response.tool_calls)
#
#     print("\nFINAL RESPONSE:")
#     print(response.final_text)
#
#
#     metric = StepEfficiencyMetric(
#         threshold=0.5,
#         model=gemini_model,
#     )
#
#     assert_test(
#         golden=golden,
#         metrics=[metric],
#     )