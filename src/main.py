import json

from llm_client import create_client
from llm import ask_llm
from evaluator import evaluate_response


POLICY = """
Customers may return unopened products within 30 days.

Opened products may be returned within 14 days
only if they are defective.

Digital products cannot be returned.

Refunds are issued to the original payment method.
"""


def load_evaluation_cases():
    with open("data/evaluation_cases_small.json", "r") as file:
        return json.load(file)


def main():
    client = create_client()

    cases = load_evaluation_cases()

    for case in cases:

        # 1. First LLM answers the customer
        ai_response = ask_llm(
            client=client,
            policy=POLICY,
            question=case["question"]
        )

        # 2. Second LLM judges the answer
        evaluation = evaluate_response(
            client=client,
            policy=POLICY,
            question=case["question"],
            ai_response=ai_response,
            evaluation_criteria=case["evaluation_criteria"]
        )

        print("\n" + "=" * 60)
        print(f"QUESTION: {case['question']}")
        print(f"\nAI RESPONSE:\n{ai_response}")
        print(f"\nJUDGE: {evaluation.result}")
        print(f"REASON: {evaluation.reason}")


if __name__ == "__main__":
    main()