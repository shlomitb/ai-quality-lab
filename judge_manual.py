import json
import os

from dotenv import load_dotenv
from google import genai

from src.evaluator import evaluate_response


POLICY = """
Customers may return unopened products within 30 days.

Opened products may be returned within 14 days
only if they are defective.

Digital products cannot be returned.

Refunds are issued to the original payment method.
"""


def load_judge_test_cases():
    with open("data/judge_test_cases.json", "r") as file:
        return json.load(file)



def main():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY was not found.")

    client = genai.Client(api_key=api_key)

    test_cases = load_judge_test_cases()

    for case in test_cases:

        evaluation = evaluate_response(
            client=client,
            policy=POLICY,
            question=case["question"],
            ai_response=case["ai_response"],
            evaluation_criteria=(
                "The AI must not assume whether the product is "
                "opened or unopened. If this information is missing, "
                "the AI should ask for clarification rather than "
                "making a return-eligibility decision."
            ),
        )

        print("\n" + "=" * 60)
        print(f"CASE: {case['id']}")
        print(f"AI RESPONSE:\n{case['ai_response']}")
        print(f"\nEXPECTED: {case['expected']}")
        print(f"ACTUAL:   {evaluation.result}")
        print(f"\nJUDGE REASON:\n{evaluation.reason}")

        if evaluation.result == case["expected"]:
            print("\n>>> CORRECT JUDGMENT")
        else:
            print("\n>>> WRONG JUDGMENT")


if __name__ == "__main__":
    main()