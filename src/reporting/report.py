from .models import (
    DeepEvalTestResult,
    JudgeTestResult,
    PytestSummary,
    QualityReport,
    QualityReportComparison,
)


def build_quality_report(
    run_id: str,
    timestamp: str,
    pytest_summary: PytestSummary | None = None,
    deepeval_results: list[DeepEvalTestResult] | None = None,
    judge: list[JudgeTestResult] | None = None,
    comparison: QualityReportComparison | None = None,
) -> QualityReport:

    return QualityReport(
        run_id=run_id,
        timestamp=timestamp,
        pytest=pytest_summary,
        deepeval=deepeval_results or [],
        judge=judge or [],
        comparison=comparison,
    )