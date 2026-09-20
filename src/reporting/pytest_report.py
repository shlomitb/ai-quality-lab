import xml.etree.ElementTree as ET
from pathlib import Path

from .models import PytestSummary


def load_pytest_summary(report_path: str | Path) -> PytestSummary:
    """
    Read a pytest JUnit XML report and return a normalized PytestSummary.
    """

    report_path = Path(report_path)

    if not report_path.exists():
        raise FileNotFoundError(
            f"Pytest report not found: {report_path}"
        )

    root = ET.parse(report_path).getroot()

    # pytest normally puts the summary information on <testsuite>
    testsuite = root.find("testsuite")

    if testsuite is None:
        raise ValueError(
            "Could not find <testsuite> in pytest report."
        )

    return PytestSummary(
        total=int(testsuite.attrib.get("tests", 0)),
        passed=(
            int(testsuite.attrib.get("tests", 0))
            - int(testsuite.attrib.get("failures", 0))
            - int(testsuite.attrib.get("errors", 0))
            - int(testsuite.attrib.get("skipped", 0))
        ),
        failed=int(testsuite.attrib.get("failures", 0)),
        skipped=int(testsuite.attrib.get("skipped", 0)),
        errors=int(testsuite.attrib.get("errors", 0)),
        duration_seconds=float(
            testsuite.attrib.get("time", 0.0)
        ),
    )