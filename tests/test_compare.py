import pytest
from src.reporting.compare import compare_quality_reports
from src.reporting.models import (
    DeepEvalMetricResult,
    DeepEvalTestResult,
    PytestSummary,
    QualityReport,
)


def test_compare_quality_reports():
    previous = QualityReport(
        run_id="run-001",
        timestamp="2026-09-22T10:00:00",
        pytest=PytestSummary(
            total=100,
            passed=98,
            failed=1,
            skipped=1,
            errors=0,
            duration_seconds=10.0,
        ),
        deepeval=[
            DeepEvalTestResult(
                name="test_agent",
                success=True,
                actual_output="Previous output",
                duration_seconds=20.0,
                metrics=[
                    DeepEvalMetricResult(
                        name="Task Completion",
                        score=1.0,
                        threshold=0.8,
                        success=True,
                        reason="Good",
                    )
                ],
            )
        ],
    )

    current = QualityReport(
        run_id="run-002",
        timestamp="2026-09-23T10:00:00",
        pytest=PytestSummary(
            total=102,
            passed=100,
            failed=0,
            skipped=2,
            errors=0,
            duration_seconds=11.0,
        ),
        deepeval=[
            DeepEvalTestResult(
                name="test_agent",
                success=True,
                actual_output="Current output",
                duration_seconds=21.0,
                metrics=[
                    DeepEvalMetricResult(
                        name="Task Completion",
                        score=0.9,
                        threshold=0.8,
                        success=True,
                        reason="Good",
                    )
                ],
            )
        ],
    )

    comparison = compare_quality_reports(previous, current)

    assert comparison.previous_run_id == "run-001"
    assert comparison.current_run_id == "run-002"

    assert comparison.pytest_changes["passed"] == 2
    assert comparison.pytest_changes["failed"] == -1
    assert comparison.pytest_changes["skipped"] == 1

    assert len(comparison.deepeval_metrics) == 1

    metric_change = comparison.deepeval_metrics[0]

    assert metric_change.name == "Task Completion"
    assert metric_change.previous == 1.0
    assert metric_change.current == 0.9
    assert metric_change.change == pytest.approx(-0.1)


def test_compare_quality_reports_handles_missing_pytest_data():
    previous = QualityReport(
        run_id="run-001",
        timestamp="2026-09-22T10:00:00",
    )

    current = QualityReport(
        run_id="run-002",
        timestamp="2026-09-23T10:00:00",
        pytest=PytestSummary(
            total=10,
            passed=10,
            failed=0,
        ),
    )

    comparison = compare_quality_reports(previous, current)

    assert comparison.pytest_changes == {}


def test_compare_quality_reports_ignores_new_deepeval_metrics():
    previous = QualityReport(
        run_id="run-001",
        timestamp="2026-09-22T10:00:00",
        deepeval=[
            DeepEvalTestResult(
                name="test_agent",
                success=True,
                actual_output="Previous output",
                duration_seconds=20.0,
                metrics=[
                    DeepEvalMetricResult(
                        name="Task Completion",
                        score=1.0,
                        threshold=0.8,
                        success=True,
                        reason="Good",
                    )
                ],
            )
        ],
    )

    current = QualityReport(
        run_id="run-002",
        timestamp="2026-09-23T10:00:00",
        deepeval=[
            DeepEvalTestResult(
                name="test_agent",
                success=True,
                actual_output="Current output",
                duration_seconds=21.0,
                metrics=[
                    DeepEvalMetricResult(
                        name="Task Completion",
                        score=0.9,
                        threshold=0.8,
                        success=True,
                        reason="Good",
                    ),
                    DeepEvalMetricResult(
                        name="Step Efficiency",
                        score=1.0,
                        threshold=0.8,
                        success=True,
                        reason="Good",
                    ),
                ],
            )
        ],
    )

    comparison = compare_quality_reports(previous, current)

    assert len(comparison.deepeval_metrics) == 1
    assert comparison.deepeval_metrics[0].name == "Task Completion"


def test_compare_quality_reports_identifies_regressions_and_improvements():
    previous = QualityReport(
        run_id="run-001",
        timestamp="2026-09-22T10:00:00",
        pytest=PytestSummary(
            total=100,
            passed=98,
            failed=2,
            skipped=0,
            errors=0,
        ),
        deepeval=[
            DeepEvalTestResult(
                name="test_agent",
                success=True,
                actual_output="Previous output",
                duration_seconds=20.0,
                metrics=[
                    DeepEvalMetricResult(
                        name="Task Completion",
                        score=1.0,
                        threshold=0.8,
                        success=True,
                        reason="Good",
                    ),
                    DeepEvalMetricResult(
                        name="Step Efficiency",
                        score=0.8,
                        threshold=0.8,
                        success=True,
                        reason="Good",
                    ),
                ],
            )
        ],
    )

    current = QualityReport(
        run_id="run-002",
        timestamp="2026-09-23T10:00:00",
        pytest=PytestSummary(
            total=100,
            passed=99,
            failed=1,
            skipped=0,
            errors=0,
        ),
        deepeval=[
            DeepEvalTestResult(
                name="test_agent",
                success=True,
                actual_output="Current output",
                duration_seconds=21.0,
                metrics=[
                    DeepEvalMetricResult(
                        name="Task Completion",
                        score=0.9,
                        threshold=0.8,
                        success=True,
                        reason="Good",
                    ),
                    DeepEvalMetricResult(
                        name="Step Efficiency",
                        score=0.9,
                        threshold=0.8,
                        success=True,
                        reason="Good",
                    ),
                ],
            )
        ],
    )

    comparison = compare_quality_reports(previous, current)

    assert "Task Completion" in comparison.regressions
    assert "Step Efficiency" in comparison.improvements
    assert "pytest failures" in comparison.improvements


def test_compare_quality_reports_ignores_unchanged_values():
    previous = QualityReport(
        run_id="run-001",
        timestamp="2026-09-22T10:00:00",
        pytest=PytestSummary(
            total=100,
            passed=99,
            failed=1,
            skipped=0,
            errors=0,
        ),
        deepeval=[
            DeepEvalTestResult(
                name="test_agent",
                success=True,
                actual_output="Previous output",
                duration_seconds=20.0,
                metrics=[
                    DeepEvalMetricResult(
                        name="Task Completion",
                        score=0.9,
                        threshold=0.8,
                        success=True,
                        reason="Good",
                    )
                ],
            )
        ],
    )

    current = QualityReport(
        run_id="run-002",
        timestamp="2026-09-23T10:00:00",
        pytest=PytestSummary(
            total=100,
            passed=99,
            failed=1,
            skipped=0,
            errors=0,
        ),
        deepeval=[
            DeepEvalTestResult(
                name="test_agent",
                success=True,
                actual_output="Current output",
                duration_seconds=21.0,
                metrics=[
                    DeepEvalMetricResult(
                        name="Task Completion",
                        score=0.9,
                        threshold=0.8,
                        success=True,
                        reason="Good",
                    )
                ],
            )
        ],
    )

    comparison = compare_quality_reports(previous, current)

    assert comparison.regressions == []
    assert comparison.improvements == []