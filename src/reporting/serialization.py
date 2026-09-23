import json
from dataclasses import asdict
from pathlib import Path

from .models import (
    DeepEvalMetricResult,
    DeepEvalTestResult,
    MetricChange,
    PytestSummary,
    QualityReport,
    QualityReportComparison,
)


def save_quality_report(
    report: QualityReport,
    output_path: str | Path,
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = asdict(report)

    output_path.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )


def load_quality_report(
    report_path: str | Path,
) -> QualityReport:
    report_path = Path(report_path)

    if not report_path.exists():
        raise FileNotFoundError(
            f"Quality report not found: {report_path}"
        )

    with report_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    pytest_data = data.get("pytest")

    pytest_summary = None

    if pytest_data is not None:
        pytest_summary = PytestSummary(**pytest_data)

    deepeval_results = []

    for test_data in data.get("deepeval", []):
        metrics = [
            DeepEvalMetricResult(**metric_data)
            for metric_data in test_data.get("metrics", [])
        ]

        deepeval_results.append(
            DeepEvalTestResult(
                name=test_data["name"],
                success=bool(test_data["success"]),
                actual_output=test_data.get("actual_output", ""),
                duration_seconds=float(
                    test_data.get("duration_seconds", 0.0)
                ),
                evaluation_cost=test_data.get("evaluation_cost"),
                metrics=metrics,
                trajectory=test_data.get("trajectory", []),
            )
        )

    comparison_data = data.get("comparison")

    comparison = None

    if comparison_data is not None:
        comparison = QualityReportComparison(
            previous_run_id=comparison_data["previous_run_id"],
            current_run_id=comparison_data["current_run_id"],
            pytest_changes=comparison_data.get(
                "pytest_changes", {}
            ),
            deepeval_metrics=[
                MetricChange(**metric_data)
                for metric_data in comparison_data.get(
                    "deepeval_metrics", []
                )
            ],
            regressions=comparison_data.get("regressions", []),
            improvements=comparison_data.get("improvements", []),
        )

    return QualityReport(
        run_id=data["run_id"],
        timestamp=data["timestamp"],
        pytest=pytest_summary,
        deepeval=deepeval_results,
        security_results=data.get("security_results", {}),
        performance=data.get("performance", {}),
        notes=data.get("notes", []),
        comparison=comparison,
    )