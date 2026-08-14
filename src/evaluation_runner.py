import json

from agent import answer_customer
from evaluator import evaluate_response
from llm_client import create_client
from tools import get_return_policy
from report_generator import generate_report



"""
Tests what the agent did.
"""


MAX_CASES = 2

FILEPATH = "../data/evaluation_cases_for_report.json"
#"../data/evaluation_cases.json"

def load_evaluation_cases():
    with open(FILEPATH) as file:
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
            "judge_result": evaluation.result,
            "reason": evaluation.reason,
        })

    generate_report(results)


if __name__ == "__main__":
    main()