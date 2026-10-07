from src.reporting.models import (
    DeepEvalMetricResult,
    DeepEvalTestResult,
    PytestSummary,
    QualityReport,
    QualityReportComparison,
    MetricChange,
)
from src.reporting.report_renderer import (
    render_markdown,
    write_markdown_report,
)


def test_render_markdown():
    """
    Verifies that a populated report produces the important sections and that the main data actually appears in the Markdown
    """
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

    assert "2026-09-20T10:00:00" in markdown
    assert "4.5" in markdown
    assert "0.0145" in markdown


def test_render_markdown_reports_repeated_tool_when_step_efficiency_fails():
    report = QualityReport(
        run_id="test-run-efficiency",
        timestamp="2026-09-20T10:00:00",
        deepeval=[
            DeepEvalTestResult(
                name="test_inefficient_agent",
                success=False,
                actual_output="The agent completed the task.",
                duration_seconds=20.0,
                metrics=[
                    DeepEvalMetricResult(
                        name="Step Efficiency",
                        score=0.75,
                        threshold=0.8,
                        success=False,
                        reason=(
                            "The agent repeated a tool unnecessarily."
                        ),
                    ),
                ],
                trajectory=[
                    "search_files",
                    "read_file",
                    "run_tests",
                    "read_file",
                    "run_tests",
                ],
            )
        ],
    )

    markdown = render_markdown(report)

    assert (
        "Efficiency concern in `test_inefficient_agent`"
        in markdown
    )

    assert "`run_tests` was called 2 times" in markdown

    assert "Step Efficiency failed" in markdown


def test_render_markdown_does_not_flag_repeated_tools_when_step_efficiency_passes():
    report = QualityReport(
        run_id="test-run-efficient",
        timestamp="2026-09-20T10:00:00",
        deepeval=[
            DeepEvalTestResult(
                name="test_efficient_agent",
                success=True,
                actual_output="The agent completed the task.",
                duration_seconds=20.0,
                metrics=[
                    DeepEvalMetricResult(
                        name="Step Efficiency",
                        score=1.0,
                        threshold=0.8,
                        success=True,
                        reason="The agent used efficient steps.",
                    ),
                ],
                trajectory=[
                    "search_files",
                    "read_file",
                    "read_file",
                    "run_tests",
                ],
            )
        ],
    )

    markdown = render_markdown(report)

    assert "Efficiency concern" not in markdown


def test_render_markdown_distinguishes_pytest_failure_from_ai_quality_failure():
    report = QualityReport(
        run_id="test-run-pytest-failure",
        timestamp="2026-09-20T10:00:00",
        pytest=PytestSummary(
            total=10,
            passed=9,
            failed=1,
            skipped=0,
            errors=0,
            duration_seconds=2.0,
        ),
        deepeval=[
            DeepEvalTestResult(
                name="test_agent",
                success=True,
                actual_output="The task was completed.",
                duration_seconds=10.0,
                metrics=[
                    DeepEvalMetricResult(
                        name="Task Completion",
                        score=1.0,
                        threshold=0.8,
                        success=True,
                        reason="The task was completed successfully.",
                    ),
                ],
            )
        ],
    )

    markdown = render_markdown(report)

    assert (
        "automated test failures detected; "
        "AI quality evaluation passed"
        in markdown
    )

def test_write_markdown_report(tmp_path):
    """
    Tests the important contract:
    """
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
                test_name="test-run-001",
                metric_name="Task Completion",
                previous=1.0,
                current=0.9,
                change=-0.1,
            ),
            MetricChange(
                test_name="test-run-001",
                metric_name="Step Efficiency",
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



def test_render_markdown_with_multiple_deepeval_tests():
    report = QualityReport(
        run_id="test-run-multiple-deepeval",
        timestamp="2026-10-07T10:53:02",
        pytest=PytestSummary(
            total=123,
            passed=102,
            failed=1,
            skipped=20,
            errors=0,
            duration_seconds=4.77,
        ),
        deepeval=[
            DeepEvalTestResult(
                name="test_bug_file_search_task_completion",
                success=True,
                actual_output=(
                    "The agent identified src/login.py."
                ),
                duration_seconds=1.2,
                evaluation_cost=0.002,
                metrics=[
                    DeepEvalMetricResult(
                        name="Task Completion",
                        score=1.0,
                        threshold=0.5,
                        success=True,
                        reason=(
                            "The task was completed successfully."
                        ),
                    ),
                ],
                trajectory=[
                    "get_ticket",
                    "request_tool_access(search_files)",
                    "search_files",
                ],
            ),
            DeepEvalTestResult(
                name="test_dynamic_tool_access_agent",
                success=False,
                actual_output=(
                    "The agent completed the review."
                ),
                duration_seconds=2.5,
                evaluation_cost=0.004,
                metrics=[
                    DeepEvalMetricResult(
                        name="Task Completion",
                        score=1.0,
                        threshold=0.5,
                        success=True,
                        reason=(
                            "The task was completed successfully."
                        ),
                    ),
                    DeepEvalMetricResult(
                        name="Step Efficiency",
                        score=0.6,
                        threshold=0.8,
                        success=False,
                        reason=(
                            "The agent repeated run_tests unnecessarily."
                        ),
                    ),
                ],
                trajectory=[
                    "get_ticket",
                    "request_tool_access(run_tests)",
                    "run_tests",
                    "run_tests",
                ],
            ),
        ],
    )

    markdown = render_markdown(report)

    # Executive summary aggregates both tests and all metrics.
    assert "DeepEval Tests | 1/2 passed" in markdown
    assert "DeepEval Metrics | 2/3 passed" in markdown

    # Both DeepEval tests appear in the detailed report.
    assert (
        "### test_bug_file_search_task_completion"
        in markdown
    )
    assert "### test_dynamic_tool_access_agent" in markdown

    # Both tests' metrics appear.
    assert "Task Completion" in markdown
    assert "Step Efficiency" in markdown
    assert "0.60" in markdown

    # Both agent trajectories appear.
    assert "request_tool_access(search_files)" in markdown
    assert "request_tool_access(run_tests)" in markdown

    # The failed efficiency metric produces the behavioral finding.
    assert (
        "Efficiency concern in "
        "`test_dynamic_tool_access_agent`"
        in markdown
    )
    assert "`run_tests` was called 2 times" in markdown
    assert "Step Efficiency failed" in markdown

    # The overall report recognizes the DeepEval failure.
    assert (
        "🔴 FAIL — AI quality evaluation failed"
        in markdown
    )