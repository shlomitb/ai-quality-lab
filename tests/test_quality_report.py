from pathlib import Path

from src.reporting.deepeval_report import load_deepeval_results
from src.reporting.pytest_report import load_pytest_summary
from src.reporting.report import build_quality_report


FIXTURES = Path(__file__).parent / "fixtures"
PYTEST_FIXTURE = FIXTURES / "pytest_sample.xml"
DEEPEVAL_FIXTURE = FIXTURES / "deepeval_sample.json"


def test_build_quality_report():
    pytest_summary = load_pytest_summary(PYTEST_FIXTURE)
    deepeval_results = load_deepeval_results(DEEPEVAL_FIXTURE)

    report = build_quality_report(
        run_id="test-run-001",
        timestamp="2026-09-23T10:00:00",
        pytest_summary=pytest_summary,
        deepeval_results=deepeval_results,
    )

    assert report.run_id == "test-run-001"
    assert report.timestamp == "2026-09-23T10:00:00"

    assert report.pytest is not None
    assert report.pytest.total == 5
    assert report.pytest.passed == 3
    assert report.pytest.failed == 1
    assert report.pytest.skipped == 1
    assert report.pytest.errors == 0
    assert report.pytest.duration_seconds == 1.25

    assert len(report.deepeval) == 1

    deep_eval = report.deepeval[0]
    assert deep_eval.name == "test_dynamic_escalation_agent"
    assert deep_eval.success is True
    assert len(deep_eval.metrics) == 2
    assert deep_eval.trajectory[-1] == "run_tests"