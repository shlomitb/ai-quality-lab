import json
from pathlib import Path

from src.evaluator import evaluate_response
from src.llm_client import create_client
from src.tools import get_return_policy


"""
Tests if the judge correctly evaluates what the agent did

The judge_test_cases.json contains hard-coded ai_responss for each case (the 1st llm call response)
And the judge is what we are testing, and this is a real llm call
In a normal run of the agent this would be 2 llm calls, the initial ai response and then the judge checks that responser.

Run with: python -m src.judge_runner
Since uses an llm call per case, to run 1 case change MAX_CASES = 1
and put the case you want to run 1st in the json list.

"""

MAX_CASES = 1

DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "judge_test_cases.json"
)


def load_judge_test_cases():
    with open(DATA_FILE) as file:
        return json.load(file)


def main():
    client = create_client()

    cases = load_judge_test_cases()
    if MAX_CASES:
        cases = cases[:MAX_CASES]

    policy = get_return_policy()

    correct = 0

    for case in cases:

        evaluation = evaluate_response(
            client=client,
            policy=policy,
            question=case["question"],
            ai_response=case["ai_response"],
            evaluation_criteria=case["evaluation_criteria"]
        )

        actual = evaluation.result
        expected = case["expected_judge_evaluation"]

        if actual == expected:
            correct += 1

        print("\n" + "=" * 60)
        print(f"ID: {case['id']}")
        print(f"TEST TYPE: {case['test_type']}")
        print(f"QUESTION: {case['question']}")
        print(f"AI RESPONSE: {case['ai_response']}")
        print(f"EXPECTED JUDGE: {expected}")
        print(f"ACTUAL JUDGE:   {actual}")

        if actual == expected:
            print("JUDGE CORRECT: YES")
        else:
            print("JUDGE CORRECT: NO")

        print(f"REASON: {evaluation.reason}")

    total = len(cases)

    print("\n" + "=" * 60)
    print("JUDGE EVALUATION REPORT")
    print("=" * 60)
    print(f"Total cases:      {total}")
    print(f"Judge correct:    {correct}/{total}")
    print(f"Judge accuracy:   {correct / total:.1%}")


if __name__ == "__main__":
    main()