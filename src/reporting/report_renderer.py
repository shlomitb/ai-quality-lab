from pathlib import Path

from .models import QualityReport


def render_markdown(report: QualityReport) -> str:
    """
    Render a QualityReport as a Markdown string.
    """

    lines = [
        "# AI Quality Report",
        "",
        "## Run Information",
        "",
        f"- **Run ID:** {report.run_id}",
        f"- **Timestamp:** {report.timestamp}",
        "",
    ]

    # ---------------------------------------------------------
    # Pytest
    # ---------------------------------------------------------

    if report.pytest is not None:
        pytest = report.pytest

        lines.extend(
            [
                "## Pytest",
                "",
                f"- **Total:** {pytest.total}",
                f"- **Passed:** {pytest.passed}",
                f"- **Failed:** {pytest.failed}",
                f"- **Skipped:** {pytest.skipped}",
                f"- **Errors:** {pytest.errors}",
                (
                    f"- **Duration:** "
                    f"{pytest.duration_seconds:.2f} seconds"
                ),
                "",
            ]
        )

    # ---------------------------------------------------------
    # DeepEval
    # ---------------------------------------------------------

    if report.deepeval:
        lines.extend(
            [
                "## DeepEval",
                "",
            ]
        )

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

    # ---------------------------------------------------------
    # Security
    # ---------------------------------------------------------

    if report.security_results:
        lines.extend(
            [
                "## Security",
                "",
            ]
        )

        for name, passed in report.security_results.items():
            status = "PASS" if passed else "FAIL"

            lines.append(
                f"- **{name}:** {status}"
            )

        lines.append("")

    # ---------------------------------------------------------
    # Performance
    # ---------------------------------------------------------

    if report.performance:
        lines.extend(
            [
                "## Performance",
                "",
            ]
        )

        for name, value in report.performance.items():
            lines.append(
                f"- **{name}:** {value}"
            )

        lines.append("")

    # ---------------------------------------------------------
    # Notes
    # ---------------------------------------------------------

    if report.notes:
        lines.extend(
            [
                "## Notes",
                "",
            ]
        )

        for note in report.notes:
            lines.append(
                f"- {note}"
            )

        lines.append("")

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