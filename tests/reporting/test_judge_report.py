import json

from src.reporting.judge_report import load_judge_results
from src.reporting.models import JudgeTestResult


def test_load_judge_results(tmp_path):
    judge_results = [
        {
            "name": "security_sensitive_information_001",
            "test_type": "sensitive_information_leakage",
            "expected": "FAIL",
            "actual": "FAIL",
            "success": True,
            "reason": (
                "Sensitive information was correctly identified."
            ),
        }
    ]

    report_path = tmp_path / "judge_results.json"

    report_path.write_text(
        json.dumps(judge_results),
        encoding="utf-8",
    )

    loaded_results = load_judge_results(report_path)

    assert loaded_results == [
        JudgeTestResult(
            name="security_sensitive_information_001",
            test_type="sensitive_information_leakage",
            expected="FAIL",
            actual="FAIL",
            success=True,
            reason=(
                "Sensitive information was correctly identified."
            ),
        )
    ]