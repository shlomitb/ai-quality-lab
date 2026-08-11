
from evaluator import evaluate_behavior


def test_clarification_response():
    response = "I need to know whether the product is opened."

    actual = evaluate_behavior(
        response,
        "ask_for_clarification"
    )

    assert actual == "ask_for_clarification"


def test_normal_answer():
    response = "Yes, you can return an unopened product within 30 days."

    actual = evaluate_behavior(
        response,
        "answer"
    )

    assert actual == "answer"


def test_different_clarification_phrase():
    response = "Could you tell me whether the product is defective?"

    actual = evaluate_behavior(
        response,
        "ask_for_clarification"
    )

    assert actual == "ask_for_clarification"


# def test_keyword_appears_but_response_is_actually_an_answer():
#     """
#     Fails based on keyword checks since keywords contain "need to know",
#     And here the prompt contains "need to know", but the prompt is actually good
#
#     This is a concrete example of why simple keyword matching isn't reliable enough for AI evaluation.
#
#     :return:
#     """
#     response = (
#         "You do not need to know whether the product is defective "
#         "because it is an unopened product within the 30-day period."
#     )
#
#     actual = evaluate_behavior(
#         response,
#         "answer"
#     )
#
#     assert actual == "answer"
