import pytest

from src.reporting.models import (
    DeepEvalMetricResult,
    DeepEvalTestResult,
    MetricChange,
    PytestSummary,
    QualityReport,
    QualityReportComparison,
)
from src.reporting.serialization import (
    load_quality_report,
    save_quality_report,
)


def test_save_and_load_quality_report(tmp_path):
    original = QualityReport(
        run_id="run-001",
        timestamp="2026-09-23T10:00:00",
        pytest=PytestSummary(
            total=10,
            passed=8,
            failed=1,
            skipped=1,
            errors=0,
            duration_seconds=1.25,
        ),
        deepeval=[
            DeepEvalTestResult(
                name="test_agent",
                success=True,
                actual_output="Test output",
                duration_seconds=20.5,
                evaluation_cost=0.01,
                metrics=[
                    DeepEvalMetricResult(
                        name="Task Completion",
                        score=0.9,
                        threshold=0.8,
                        success=True,
                        reason="Good",
                    )
                ],
                trajectory=[
                    "search_files",
                    "read_file",
                    "run_tests",
                ],
            )
        ],
        security_results={
            "unauthorized_tool_access": True,
        },
        performance={
            "duration_seconds": 20.5,
        },
        notes=["Test note"],
        comparison=QualityReportComparison(
            previous_run_id="run-000",
            current_run_id="run-001",
            pytest_changes={
                "passed": 1,
                "failed": -1,
            },
            deepeval_metrics=[
                MetricChange(
                    name="Task Completion",
                    previous=0.8,
                    current=0.9,
                    change=0.1,
                )
            ],
            regressions=[],
            improvements=["Task Completion"],
        ),
    )

    output_path = tmp_path / "quality_report.json"

    save_quality_report(original, output_path)

    loaded = load_quality_report(output_path)

    assert loaded == original


def test_load_quality_report_raises_for_missing_file(tmp_path):
    report_path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_quality_report(report_path)