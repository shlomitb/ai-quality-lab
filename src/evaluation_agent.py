import json

from agent import answer_customer
from evaluator import evaluate_response
from llm_client import create_client
from tools import get_return_policy


def load_evaluation_cases():
    with open("../data/evaluation_cases.json") as file:
        return json.load(file)


def main():

    client = create_client()

    cases = load_evaluation_cases()

    # Get the policy once
    policy = get_return_policy()

    case = cases[4]
    question = case["question"]
    # 1. Run the agent
    ai_response = answer_customer(
        client=client,
        question=question
    )

    # 2. Judge the agent's response
    evaluation = evaluate_response(
        client=client,
        policy=policy,
        question=question,
        ai_response=ai_response,
        evaluation_criteria=case["evaluation_criteria"]
    )

    print("\n" + "=" * 60)
    print(f"QUESTION: {question}")
    print(f"\nAI RESPONSE:\n{ai_response}")
    print(f"\nJUDGE: {evaluation.result}")
    print(f"REASON: {evaluation.reason}")

    print(f"EXPECTED BEHAVIOR: {case['expected_behavior']}")
    print(f"EXPECTED ANSWER:   {case['expected']}")
    print(f"JUDGE RESULT:      {evaluation.result}")

    expected_judge_result = case["expected_judge_evaluation"]

    if evaluation.result == expected_judge_result:
        print("JUDGE CORRECT: YES")
    else:
        print("JUDGE CORRECT: NO")


if __name__ == "__main__":
    main()