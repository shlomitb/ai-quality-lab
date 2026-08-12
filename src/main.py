
import os

from dotenv import load_dotenv
from google import genai

from evaluator import evaluate_response


POLICY = """
Customers may return unopened products within 30 days.

Opened products may be returned within 14 days
only if they are defective.

Digital products cannot be returned.

Refunds are issued to the original payment method.
"""


def main():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY was not found.")

    client = genai.Client(api_key=api_key)

    # -------------------------------------------------
    # Test 1: This response should PASS
    # -------------------------------------------------

    question = "I bought the product 10 days ago. Can I return it?"

    ai_response = (
        "I need to know whether the product is opened or unopened "
        "before I can determine whether it can be returned."
    )

    evaluation_criteria = (
        "The AI should not guess because the question does not "
        "specify whether the product is opened or unopened. "
        "It should ask for the missing information."
    )

    result = evaluate_response(
        client,
        POLICY,
        question,
        ai_response,
        evaluation_criteria
    )

    print("\n--- TEST 1 ---")
    print("Result:", result.result)
    print("Reason:", result.reason)

    # -------------------------------------------------
    # Test 2: This response should FAIL
    # -------------------------------------------------

    question = "I bought the product 10 days ago. Can I return it?"

    ai_response = (
        "Yes, you can return it because it is within the "
        "30-day return period."
    )

    result = evaluate_response(
        client,
        POLICY,
        question,
        ai_response,
        evaluation_criteria
    )

    print("\n--- TEST 2 ---")
    print("Result:", result.result)
    print("Reason:", result.reason)


if __name__ == "__main__":
    main()

