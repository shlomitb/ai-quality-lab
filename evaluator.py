"""
    Requirement: Handling insufficient information

    When the policy does not contain enough information
    to determine an answer:

    1. The AI must not make an unsupported assumption.
    2. The AI must explain what information is missing.
    3. The AI must ask the customer for the missing information.

    Simple keyword matching is not a reliable enough way to test for AI evaluation.
    Since the response could contain a keyword phrase that is in a different context, when the response may be good.
"""


CLARIFICATION_KEYWORDS = [
    "need to know",
    "more information",
    "please tell me",
    "could you tell me",
]

def evaluate_behavior(response, expected_behavior):
    for phrase in CLARIFICATION_KEYWORDS:
        if phrase in response.lower():
            return "ask_for_clarification"
    return "answer"



def main():
    print(evaluate_behavior(
        "I need to know whether the product is opened.",
        "ask_for_clarification"
    ))

    print(evaluate_behavior(
        "Yes, you can return the unopened product within 30 days.",
        "answer"
    ))

    print(evaluate_behavior(
        "Could you tell me whether the product is defective?",
        "ask_for_clarification"
    ))


if __name__ == "__main__":
    main()