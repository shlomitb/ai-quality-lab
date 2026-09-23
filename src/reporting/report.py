from .models import (
    DeepEvalTestResult,
    PytestSummary,
    QualityReport,
    QualityReportComparison,
)


def build_quality_report(
    run_id: str,
    timestamp: str,
    pytest_summary: PytestSummary | None = None,
    deepeval_results: list[DeepEvalTestResult] | None = None,
    comparison: QualityReportComparison | None = None,
) -> QualityReport:
    """
    Combine normalized pytest and DeepEval results
    into one project-level quality report.
    """

    return QualityReport(
        run_id=run_id,
        timestamp=timestamp,
        pytest=pytest_summary,
        deepeval=deepeval_results or [],
        comparison=comparison,
    )