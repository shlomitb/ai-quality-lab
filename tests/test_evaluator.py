
from src.evaluator import evaluate_behavior

"""
This test file tests rule-based behavior evaluator (with keywords)
"""

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


def test_clarification_uppercase():
    response = "I NEED TO KNOW whether the product is opened."

    actual = evaluate_behavior(
        response,
        "ask_for_clarification"
    )

    assert actual == "ask_for_clarification"


def test_clarification_phrase_in_middle_of_response():
    response = (
        "Before I can answer, I need to know whether "
        "the product is opened or unopened."
    )

    actual = evaluate_behavior(
        response,
        "ask_for_clarification"
    )

    assert actual == "ask_for_clarification"


# def test_clarification_without_known_keyword():
#     """
#     test case failed on a flase negtive, since none of these were in the keywords:
#     "Was the product opened, and if so, was it defective?"
#     so answer is returned
#
#     the test is doing its job
#     :return:
#     """
#     response = (
#         "Was the product opened, and if so, was it defective?"
#     )
#
#     actual = evaluate_behavior(
#         response,
#         "ask_for_clarification"
#     )
#
#     assert actual == "ask_for_clarification"



# def test_keyword_in_answer_does_not_mean_clarification():
#     """
#     False failure since the current evaluator finds these keywords ""need to know"
#     and then concludes: ask_for_clarification
#
#     It doesn't understand the meaning or context of the phrase.

#     A false positive
#     """
#     response = (
#         "You need to know that unopened products can be returned "
#         "within 30 days."
#     )
#
#     actual = evaluate_behavior(
#         response,
#         "answer"
#     )
#
#     assert actual == "answer"