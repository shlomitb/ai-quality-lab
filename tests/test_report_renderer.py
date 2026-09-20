from src.reporting.models import (
    DeepEvalMetricResult,
    DeepEvalTestResult,
    PytestSummary,
    QualityReport,
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
                name="test_dynamic_escalation_agent",
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
                    "request_tool_escalation(run_tests)",
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
    assert "test_dynamic_escalation_agent" in markdown
    assert "Task Completion" in markdown
    assert "Step Efficiency" in markdown

    assert "search_files" in markdown
    assert "read_file" in markdown
    assert "request_tool_escalation(run_tests)" in markdown
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