import pytest

from src.reporting.pytest_report import load_pytest_summary


def test_load_pytest_summary():
    summary = load_pytest_summary(
        "reports/pytest/junit.xml"
    )

    assert summary.total == 113
    assert summary.failed == 1
    assert summary.skipped == 20
    assert summary.errors == 0
    assert summary.duration_seconds == 4.057
    assert summary.passed == 92



def test_load_pytest_summary_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_pytest_summary("does-not-exist.xml")


def test_load_pytest_summary_missing_testsuite(tmp_path):
    report_file = tmp_path / "bad_report.xml"

    report_file.write_text(
        '<?xml version="1.0" encoding="utf-8"?><testsuites></testsuites>',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Could not find <testsuite>"):
        load_pytest_summary(report_file)