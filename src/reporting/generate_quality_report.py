from datetime import datetime
from pathlib import Path

from .compare import compare_quality_reports
from .deepeval_report import load_deepeval_results
from .pytest_report import load_pytest_summary
from .report import build_quality_report
from .report_renderer import write_markdown_report
from .serialization import load_quality_report, save_quality_report


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PYTEST_REPORT = PROJECT_ROOT / "reports" / "pytest" / "junit.xml"

DEEPEVAL_REPORT_DIR = (
    PROJECT_ROOT / "reports" / "deepeval"
)

SUMMARY_DIR = (
    PROJECT_ROOT
    / "reports"
    / "summary"
)

HISTORY_DIR = SUMMARY_DIR / "history"

OUTPUT_REPORT = SUMMARY_DIR / "ai_quality_report.md"


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


def find_previous_quality_report(
    current_run_id: str,
) -> Path | None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    reports = [
        path
        for path in HISTORY_DIR.glob("*.json")
        if path.stem != current_run_id
    ]

    if not reports:
        return None

    return max(
        reports,
        key=lambda path: path.stat().st_mtime,
    )


def generate_quality_report() -> Path:
    deepeval_report = find_latest_deepeval_report()

    pytest_summary = load_pytest_summary(PYTEST_REPORT)
    deepeval_results = load_deepeval_results(deepeval_report)

    # Create a unique ID for this quality-report run.
    now = datetime.now()

    run_id = now.strftime(
        "run_%Y%m%d_%H%M%S"
    )

    timestamp = now.isoformat()

    current_report = build_quality_report(
        run_id=run_id,
        timestamp=timestamp,
        pytest_summary=pytest_summary,
        deepeval_results=deepeval_results,
    )

    # Look for the most recent previous quality report.
    previous_report_path = find_previous_quality_report(
        current_run_id=run_id
    )

    if previous_report_path is not None:
        previous_report = load_quality_report(
            previous_report_path
        )

        comparison = compare_quality_reports(
            previous=previous_report,
            current=current_report,
        )

        current_report.comparison = comparison

    # Save this run in the history.
    current_report_path = (
        HISTORY_DIR / f"{run_id}.json"
    )

    save_quality_report(
        report=current_report,
        output_path=current_report_path,
    )

    # Write the human-readable current report.
    write_markdown_report(
        report=current_report,
        output_path=OUTPUT_REPORT,
    )

    return OUTPUT_REPORT


if __name__ == "__main__":
    report_path = generate_quality_report()
    print(f"Report generated: {report_path}")