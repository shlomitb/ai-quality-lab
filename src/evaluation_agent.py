import json

from agent import answer_customer
from evaluator import evaluate_response
from llm_client import create_client
from tools import get_return_policy
from report_generator import generate_report


MAX_CASES = 4

def load_evaluation_cases():
    with open("../data/evaluation_cases.json") as file:
        return json.load(file)


def main():
    client = create_client()
    cases = load_evaluation_cases()
    if MAX_CASES:
        cases = cases[:MAX_CASES]

    policy = get_return_policy()

    results = []

    for case in cases:
        ai_response = answer_customer(
            client=client,
            question=case["question"]
        )

        evaluation = evaluate_response(
            client=client,
            policy=policy,
            question=case["question"],
            ai_response=ai_response,
            evaluation_criteria=case["evaluation_criteria"]
        )

        results.append({
            "question": case["question"],
            "expected_behavior": case["expected_behavior"],
            "actual_behavior": evaluation.behavior,
            "behavior_correct": (
                evaluation.behavior == case["expected_behavior"]
            ),
            "expected_answer": case["expected"],
            "actual_answer": evaluation.answer,
            "answer_correct": (
                evaluation.answer == case["expected"]
            ),
            "expected_judge": case["expected_judge_evaluation"],
            "actual_judge": evaluation.result,
            "judge_correct": (
                evaluation.result == case["expected_judge_evaluation"]
            ),
            "reason": evaluation.reason,
        })

    generate_report(results)


if __name__ == "__main__":
    main()