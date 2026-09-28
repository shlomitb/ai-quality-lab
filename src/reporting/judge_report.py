import json
from pathlib import Path

from .models import JudgeTestResult


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