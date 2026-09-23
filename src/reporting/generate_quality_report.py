from datetime import datetime
from pathlib import Path

from .deepeval_report import load_deepeval_results
from .pytest_report import load_pytest_summary
from .report import build_quality_report
from .report_renderer import write_markdown_report


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PYTEST_REPORT = PROJECT_ROOT / "reports" / "pytest" / "junit.xml"
DEEPEVAL_REPORT_DIR = PROJECT_ROOT / "reports" / "deepeval"
OUTPUT_REPORT = (
    PROJECT_ROOT
    / "reports"
    / "summary"
    / "ai_quality_report.md"
)


def find_latest_deepeval_report() -> Path:
    """Find the newest non-empty DeepEval JSON report."""

    reports = [
        path
        for path in DEEPEVAL_REPORT_DIR.glob("*.json")
        if path.stat().st_size > 0
    ]

    if not reports:
        raise FileNotFoundError(
            "No non-empty DeepEval JSON report was found."
        )

    return max(
        reports,
        key=lambda path: path.stat().st_mtime,
    )


def generate_quality_report() -> Path:
    """Build the combined AI quality report."""

    deepeval_report = find_latest_deepeval_report()

    pytest_summary = load_pytest_summary(
        PYTEST_REPORT
    )

    deepeval_results = load_deepeval_results(
        deepeval_report
    )

    run_id = deepeval_report.stem

    timestamp = datetime.fromtimestamp(
        deepeval_report.stat().st_mtime
    ).isoformat()

    report = build_quality_report(
        run_id=run_id,
        timestamp=timestamp,
        pytest_summary=pytest_summary,
        deepeval_results=deepeval_results,
    )

    write_markdown_report(
        report=report,
        output_path=OUTPUT_REPORT,
    )

    return OUTPUT_REPORT


if __name__ == "__main__":
    report_path = generate_quality_report()
    print(f"Report generated: {report_path}")