import json
from pathlib import Path

from src.reporting.models import JudgeTestResult


def load_judge_results(
    report_path: str | Path,
) -> list[JudgeTestResult]:
    """
    Read the judge results JSON and convert it into
    normalized JudgeTestResult objects.
    """

    report_path = Path(report_path)

    if not report_path.exists():
        raise FileNotFoundError(
            f"Judge report not found: {report_path}"
        )

    with report_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    results = []

    for test_result in data:
        results.append(
            JudgeTestResult(
                name=test_result["name"],
                test_type=test_result["test_type"],
                expected=test_result["expected"],
                actual=test_result["actual"],
                success=bool(test_result["success"]),
                reason=test_result.get("reason", ""),
            )
        )

    return results


def save_judge_results(
    results: list[JudgeTestResult],
    output_path: str | Path,
) -> None:
    """
    Save normalized judge results as JSON.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = [
        {
            "name": result.name,
            "test_type": result.test_type,
            "expected": result.expected,
            "actual": result.actual,
            "success": result.success,
            "reason": result.reason,
        }
        for result in results
    ]

    output_path.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )