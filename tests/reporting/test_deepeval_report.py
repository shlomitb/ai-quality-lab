import json
import pytest

from pathlib import Path
from src.reporting.deepeval_report import load_deepeval_results


FIXTURE = (
    Path(__file__).parent
    / ".."
    / "fixtures"
    / "deepeval_sample.json"
)


def test_load_deepeval_results():
    results = load_deepeval_results(FIXTURE)

    assert len(results) == 1

    result = results[0]

    assert result.name == "test_dynamic_escalation_agent"
    assert result.success is True

    assert result.trajectory == [
        "search_files",
        "read_file",
        "read_file",
        "request_tool_escalation(run_tests)",
        "run_tests",
    ]

    assert result.metrics[0].name == "Task Completion"
    assert result.metrics[0].score == 1.0
    assert result.metrics[0].threshold == 0.8

    assert result.metrics[1].name == "Step Efficiency"
    assert result.metrics[1].score == 1.0

    assert result.evaluation_cost == 0.0145


def test_load_deepeval_results_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_deepeval_results("does-not-exist.json")


def test_load_deepeval_results_invalid_json(tmp_path):
    report_file = tmp_path / "bad_report.json"

    report_file.write_text(
        "this is not valid JSON",
        encoding="utf-8",
    )

    with pytest.raises(json.JSONDecodeError):
        load_deepeval_results(report_file)


def test_load_deepeval_results_missing_test_cases(tmp_path):
    report_file = tmp_path / "missing_test_cases.json"

    report_file.write_text(
        '{"someOtherField": "value"}',
        encoding="utf-8",
    )

    results = load_deepeval_results(report_file)

    assert results == []