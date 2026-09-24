from src.reporting.models import (
    DeepEvalMetricResult,
    DeepEvalTestResult,
    PytestSummary,
    QualityReport,
    QualityReportComparison,
    MetricChange,
)
from src.reporting.report_renderer import render_markdown
from src.reporting.report_renderer import write_markdown_report


def test_render_markdown():
    report = QualityReport(
        run_id="test-run-001",
        timestamp="2026-09-20T10:00:00",
        pytest=PytestSummary(
            total=100,
            passed=95,
            failed=2,
            skipped=3,
            errors=0,
            duration_seconds=4.5,
        ),
        deepeval=[
            DeepEvalTestResult(
                name="test_dynamic_tool_access_agent",
                success=True,
                actual_output="The agent completed the review.",
                duration_seconds=30.2,
                evaluation_cost=0.0145,
                metrics=[
                    DeepEvalMetricResult(
                        name="Task Completion",
                        score=1.0,
                        threshold=0.8,
                        success=True,
                        reason="The task was completed.",
                        evaluation_model="gemini-3.5-flash-lite",
                        evaluation_cost=0.005,
                        input_tokens=1000,
                        output_tokens=100,
                    ),
                    DeepEvalMetricResult(
                        name="Step Efficiency",
                        score=1.0,
                        threshold=0.8,
                        success=True,
                        reason="The agent used the necessary steps.",
                        evaluation_model="gemini-3.5-flash-lite",
                        evaluation_cost=0.0095,
                        input_tokens=2000,
                        output_tokens=100,
                    ),
                ],
                trajectory=[
                    "search_files",
                    "read_file",
                    "read_file",
                    "request_tool_access(run_tests)",
                    "run_tests",
                ],
            )
        ],
    )

    markdown = render_markdown(report)

    assert "# AI Quality Report" in markdown
    assert "test-run-001" in markdown
    assert "## Pytest" in markdown
    assert "**Total:** 100" in markdown
    assert "**Passed:** 95" in markdown
    assert "**Failed:** 2" in markdown

    assert "## DeepEval" in markdown
    assert "test_dynamic_tool_access_agent" in markdown
    assert "Task Completion" in markdown
    assert "Step Efficiency" in markdown

    assert "search_files" in markdown
    assert "read_file" in markdown
    assert "request_tool_access(run_tests)" in markdown
    assert "run_tests" in markdown


def test_write_markdown_report(tmp_path):
    report = QualityReport(
        run_id="test-run-001",
        timestamp="2026-09-20T10:00:00",
    )

    output_file = tmp_path / "ai_quality_report.md"

    write_markdown_report(report, output_file)

    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")

    assert "# AI Quality Report" in content
    assert "test-run-001" in content


def test_render_markdown_includes_comparison():
    previous = QualityReport(
        run_id="run-001",
        timestamp="2026-09-22T10:00:00",
    )

    current = QualityReport(
        run_id="run-002",
        timestamp="2026-09-23T10:00:00",
    )

    comparison = QualityReportComparison(
        previous_run_id=previous.run_id,
        current_run_id=current.run_id,
        pytest_changes={
            "passed": 2,
            "failed": -1,
            "skipped": 1,
        },
        deepeval_metrics=[
            MetricChange(
                name="Task Completion",
                previous=1.0,
                current=0.9,
                change=-0.1,
            ),
            MetricChange(
                name="Step Efficiency",
                previous=0.8,
                current=0.9,
                change=0.1,
            ),
        ],
        regressions=["Task Completion"],
        improvements=["Step Efficiency", "pytest failures"],
    )

    current.comparison = comparison

    markdown = render_markdown(current)

    assert "## Comparison With Previous Run" in markdown
    assert "run-001" in markdown
    assert "Task Completion" in markdown
    assert "1.00" in markdown
    assert "0.90" in markdown
    assert "Step Efficiency" in markdown
    assert "### Regressions" in markdown
    assert "### Improvements" in markdown
    assert "pytest failures" in markdown