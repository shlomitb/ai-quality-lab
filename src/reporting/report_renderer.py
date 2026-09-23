from pathlib import Path

from .models import QualityReport

#report_renderer is only responsible for presentation.


def _render_run_information(report: QualityReport) -> list[str]:
    return [
        "# AI Quality Report",
        "",
        "## Run Information",
        "",
        f"- **Run ID:** {report.run_id}",
        f"- **Timestamp:** {report.timestamp}",
        "",
    ]


def _render_pytest(report: QualityReport) -> list[str]:
    if report.pytest is None:
        return []

    pytest = report.pytest

    return [
        "## Pytest",
        "",
        f"- **Total:** {pytest.total}",
        f"- **Passed:** {pytest.passed}",
        f"- **Failed:** {pytest.failed}",
        f"- **Skipped:** {pytest.skipped}",
        f"- **Errors:** {pytest.errors}",
        f"- **Duration:** {pytest.duration_seconds:.2f} seconds",
        "",
    ]


def _render_deepeval(report: QualityReport) -> list[str]:
    if not report.deepeval:
        return []

    lines = [
        "## DeepEval",
        "",
    ]

    for test_result in report.deepeval:
        status = "PASS" if test_result.success else "FAIL"

        lines.extend(
            [
                f"### {test_result.name}",
                "",
                f"- **Status:** {status}",
                f"- **Duration:** "
                f"{test_result.duration_seconds:.2f} seconds",
            ]
        )

        if test_result.evaluation_cost is not None:
            lines.append(
                f"- **Evaluation cost:** "
                f"${test_result.evaluation_cost:.4f}"
            )

        lines.extend(
            [
                "",
                "#### Metrics",
                "",
                "| Metric | Score | Threshold | Status |",
                "|---|---:|---:|---|",
            ]
        )

        for metric in test_result.metrics:
            metric_status = (
                "PASS" if metric.success else "FAIL"
            )

            lines.append(
                f"| {metric.name} "
                f"| {metric.score:.2f} "
                f"| {metric.threshold:.2f} "
                f"| {metric_status} |"
            )

        lines.extend(
            [
                "",
                "#### Agent Trajectory",
                "",
            ]
        )

        if test_result.trajectory:
            for index, step in enumerate(
                test_result.trajectory,
                start=1,
            ):
                lines.append(
                    f"{index}. `{step}`"
                )
        else:
            lines.append(
                "No trajectory data available."
            )

        lines.append("")

        lines.extend(
            [
                "#### Metric Reasons",
                "",
            ]
        )

        for metric in test_result.metrics:
            lines.extend(
                [
                    f"**{metric.name}:** "
                    f"{metric.reason}",
                    "",
                ]
            )

    return lines


def _render_security(report: QualityReport) -> list[str]:
    if not report.security_results:
        return []

    lines = [
        "## Security",
        "",
    ]

    for name, passed in report.security_results.items():
        status = "PASS" if passed else "FAIL"

        lines.append(
            f"- **{name}:** {status}"
        )

    lines.append("")

    return lines


def _render_performance(report: QualityReport) -> list[str]:
    if not report.performance:
        return []

    lines = [
        "## Performance",
        "",
    ]

    for name, value in report.performance.items():
        lines.append(
            f"- **{name}:** {value}"
        )

    lines.append("")

    return lines


def _render_notes(report: QualityReport) -> list[str]:
    if not report.notes:
        return []

    lines = [
        "## Notes",
        "",
    ]

    for note in report.notes:
        lines.append(
            f"- {note}"
        )

    lines.append("")

    return lines


def _render_comparison(report: QualityReport) -> list[str]:
    if report.comparison is None:
        return []

    comparison = report.comparison

    lines = [
        "## Comparison With Previous Run",
        "",
        f"- **Previous run:** "
        f"{comparison.previous_run_id}",
        f"- **Current run:** "
        f"{comparison.current_run_id}",
        "",
    ]

    if comparison.pytest_changes:
        lines.extend(
            [
                "### Pytest Changes",
                "",
                "| Metric | Change |",
                "|---|---:|",
            ]
        )

        for name, change in comparison.pytest_changes.items():
            lines.append(
                f"| {name} | {change:+d} |"
            )

        lines.append("")

    if comparison.deepeval_metrics:
        lines.extend(
            [
                "### DeepEval Changes",
                "",
                "| Metric | Previous | Current | Change |",
                "|---|---:|---:|---:|",
            ]
        )

        for metric in comparison.deepeval_metrics:
            lines.append(
                f"| {metric.name} | "
                f"{metric.previous:.2f} | "
                f"{metric.current:.2f} | "
                f"{metric.change:+.2f} |"
            )

        lines.append("")

    if comparison.regressions:
        lines.extend(
            [
                "### Regressions",
                "",
            ]
        )

        for regression in comparison.regressions:
            lines.append(
                f"- {regression}"
            )

        lines.append("")

    if comparison.improvements:
        lines.extend(
            [
                "### Improvements",
                "",
            ]
        )

        for improvement in comparison.improvements:
            lines.append(
                f"- {improvement}"
            )

        lines.append("")

    return lines


def render_markdown(report: QualityReport) -> str:
    """
    Render a QualityReport as a Markdown string.
    """

    lines = _render_run_information(report)
    lines.extend(_render_pytest(report))
    lines.extend(_render_deepeval(report))
    lines.extend(_render_security(report))
    lines.extend(_render_performance(report))
    lines.extend(_render_notes(report))
    lines.extend(_render_comparison(report))

    return "\n".join(lines)


def write_markdown_report(
    report: QualityReport,
    output_path: str | Path,
) -> None:
    """
    Render a QualityReport as Markdown and write it to a file.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    markdown = render_markdown(report)

    output_path.write_text(
        markdown,
        encoding="utf-8",
    )