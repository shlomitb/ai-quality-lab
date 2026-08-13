from llm_client import create_client
from agent import answer_customer
from evaluator import evaluate_response


POLICY = """
Customers may return unopened products within 30 days.

Opened products may be returned within 14 days
only if they are defective.

Digital products cannot be returned.

Refunds are issued to the original payment method.
"""


def main():

    client = create_client()

    # One customer question for now
    question = "I bought the product 10 days ago. Can I return it?"

    evaluation_criteria = (
        "The AI should not guess because the question does not "
        "specify whether the product is opened or unopened. "
        "It should ask for the missing information."
    )

    # 1. Agent answers the customer
    ai_response = answer_customer(
        client=client,
        policy=POLICY,
        question=question
    )

    print("\nAI RESPONSE:")
    print(ai_response)

    # 2. Judge evaluates the agent's response
    evaluation = evaluate_response(
        client=client,
        policy=POLICY,
        question=question,
        ai_response=ai_response,
        evaluation_criteria=evaluation_criteria
    )

    print("\nJUDGE:")
    print(evaluation.result)

    print("\nREASON:")
    print(evaluation.reason)


if __name__ == "__main__":
    main()