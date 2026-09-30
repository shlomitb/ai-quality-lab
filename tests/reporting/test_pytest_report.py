
import pytest
import xml.etree.ElementTree as ET

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


def test_load_pytest_summary_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_pytest_summary("does-not-exist.xml")


def test_load_pytest_summary_invalid_xml(tmp_path):
    report_file = tmp_path / "bad_report.xml"

    report_file.write_text(
        "this is not valid XML",
        encoding="utf-8",
    )

    with pytest.raises(ET.ParseError):
        load_pytest_summary(report_file)