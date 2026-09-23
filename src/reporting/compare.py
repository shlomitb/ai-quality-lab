from .models import MetricChange, QualityReport, QualityReportComparison


def compare_quality_reports(
    previous: QualityReport,
    current: QualityReport,
) -> QualityReportComparison:
    comparison = QualityReportComparison(
        previous_run_id=previous.run_id,
        current_run_id=current.run_id,
    )

    if previous.pytest is not None and current.pytest is not None:
        comparison.pytest_changes = {
            "total": current.pytest.total - previous.pytest.total,
            "passed": current.pytest.passed - previous.pytest.passed,
            "failed": current.pytest.failed - previous.pytest.failed,
            "skipped": current.pytest.skipped - previous.pytest.skipped,
            "errors": current.pytest.errors - previous.pytest.errors,
        }

        if comparison.pytest_changes["failed"] < 0:
            comparison.improvements.append("pytest failures")
        elif comparison.pytest_changes["failed"] > 0:
            comparison.regressions.append("pytest failures")

    previous_metrics = {}

    for test_result in previous.deepeval:
        for metric in test_result.metrics:
            previous_metrics[(test_result.name, metric.name)] = metric.score

    for test_result in current.deepeval:
        for metric in test_result.metrics:
            key = (test_result.name, metric.name)

            if key in previous_metrics:
                previous_score = previous_metrics[key]
                current_score = metric.score
                change = current_score - previous_score

                comparison.deepeval_metrics.append(
                    MetricChange(
                        name=metric.name,
                        previous=previous_score,
                        current=current_score,
                        change=change,
                    )
                )

                if change < 0:
                    comparison.regressions.append(metric.name)
                elif change > 0:
                    comparison.improvements.append(metric.name)

    return comparison