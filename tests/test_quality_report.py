from src.reporting.deepeval_report import load_deepeval_results
from src.reporting.pytest_report import load_pytest_summary
from src.reporting.report import build_quality_report


def test_build_quality_report():
    pytest_summary = load_pytest_summary(
        "reports/pytest/junit.xml"
    )

    deepeval_results = load_deepeval_results(
        "tests/fixtures/deepeval_sample.json"
    )

    report = build_quality_report(
        run_id="test-run-001",
        timestamp="2026-09-19T20:30:00",
        pytest_summary=pytest_summary,
        deepeval_results=deepeval_results,
    )

    assert report.run_id == "test-run-001"
    assert report.timestamp == "2026-09-19T20:30:00"

    assert report.pytest is not None
    assert report.pytest.total == 113
    assert report.pytest.failed == 1

    assert len(report.deepeval) == 1
    assert report.deepeval[0].name == "test_dynamic_escalation_agent"
    assert report.deepeval[0].success is True