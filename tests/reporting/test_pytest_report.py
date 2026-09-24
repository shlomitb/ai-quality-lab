from pathlib import Path

from src.reporting.pytest_report import load_pytest_summary


FIXTURE = Path(__file__).parent / ".." / "fixtures" / "pytest_sample.xml"


def test_load_pytest_summary():
    summary = load_pytest_summary(FIXTURE)

    assert summary.total == 5
    assert summary.passed == 3
    assert summary.failed == 1
    assert summary.skipped == 1
    assert summary.errors == 0
    assert summary.duration_seconds == 1.25