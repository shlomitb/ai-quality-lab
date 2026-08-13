
from metrics import behavior_accuracy, answer_accuracy, judge_accuracy


def generate_report(results):
    total = len(results)

    behavior_correct = sum(
        result["behavior_correct"]
        for result in results
    )

    answer_correct = sum(
        result["answer_correct"]
        for result in results
    )

    judge_correct = sum(
        result["judge_correct"]
        for result in results
    )

    print("\n" + "=" * 60)
    print("AGENT EVALUATION REPORT")
    print("=" * 60)

    print(f"Total cases:       {total}")
    print(f"Behavior correct:  {behavior_correct}/{total}")
    print(f"Answer correct:    {answer_correct}/{total}")
    print(f"Judge correct:     {judge_correct}/{total}")

    failures = [
        result for result in results
        if not (
                result["behavior_correct"]
                and result["answer_correct"]
                and result["judge_correct"]
        )
    ]

    print("\nFAILURES")
    print("-" * 60)

    if not failures:
        print("None")
    else:
        for result in failures:
            print(f"\nQuestion: {result['question']}")

            if not result["behavior_correct"]:
                print(
                    f"Behavior: expected {result['expected_behavior']}, "
                    f"got {result['actual_behavior']}"
                )

            if not result["answer_correct"]:
                print(
                    f"Answer: expected {result['expected_answer']}, "
                    f"got {result['actual_answer']}"
                )

            if not result["judge_correct"]:
                print(
                    f"Judge: expected {result['expected_judge']}, "
                    f"got {result['actual_judge']}"
                )

            print(f"Reason: {result['reason']}")