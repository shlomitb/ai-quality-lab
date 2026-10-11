"""
Run this file to create the report:
python -m src.reporting.generate_quality_report
"""


import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from .compare import compare_quality_reports
from .deepeval_report import load_deepeval_results
from .judge_report import load_judge_results
from .pytest_report import load_pytest_summary
from .report import build_quality_report
from .report_renderer import write_markdown_report
from .serialization import load_quality_report, save_quality_report




PROJECT_ROOT = Path(__file__).resolve().parents[2]

PYTEST_REPORT = PROJECT_ROOT / "reports" / "pytest" / "junit.xml"

DEEPEVAL_REPORT = (
    PROJECT_ROOT / ".deepeval" / ".latest_test_run.json"
)

JUDGE_REPORT = (
    PROJECT_ROOT / "reports" / "judge" / "judge_results.json"
)

SUMMARY_DIR = (
    PROJECT_ROOT
    / "reports"
    / "summary"
)

HISTORY_DIR = SUMMARY_DIR / "history"

OUTPUT_REPORT = SUMMARY_DIR / "ai_quality_report.md"



def run_pytest() -> None:
    """Run the main deterministic test suite and refresh its JUnit XML report."""
    PYTEST_REPORT.parent.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "--ignore=demo_repo",
        f"--junitxml={PYTEST_REPORT}",
    ]

    print("Running the deterministic Pytest suite...")

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=False,
    )

    if result.returncode not in (0, 1):
        raise RuntimeError(
            f"Pytest could not complete successfully "
            f"(exit code {result.returncode})."
        )

    print("Pytest results written to:", PYTEST_REPORT)



def find_latest_deepeval_report() -> Path:
    """Return the current structured DeepEval JSON report."""

    if not DEEPEVAL_REPORT.exists():
        raise FileNotFoundError(
            f"DeepEval report not found: {DEEPEVAL_REPORT}"
        )

    if DEEPEVAL_REPORT.stat().st_size == 0:
        raise FileNotFoundError(
            f"DeepEval report is empty: {DEEPEVAL_REPORT}"
        )

    return DEEPEVAL_REPORT


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


def get_file_timestamp(path: Path) -> str | None:
    """Return a file's last-modified timestamp, or None if unavailable."""
    if not path.exists():
        return None

    return datetime.fromtimestamp(
        path.stat().st_mtime
    ).astimezone().isoformat()



def generate_quality_report() -> Path:
    deepeval_report = find_latest_deepeval_report()

    pytest_summary = load_pytest_summary(PYTEST_REPORT)
    deepeval_results = load_deepeval_results(deepeval_report)
    judge_results = load_judge_results(JUDGE_REPORT)

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
        judge=judge_results,
        pytest_timestamp=get_file_timestamp(PYTEST_REPORT),
        deepeval_timestamp=get_file_timestamp(deepeval_report),
        judge_timestamp=get_file_timestamp(JUDGE_REPORT),
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
    parser = argparse.ArgumentParser(
        description="Generate the AI quality report."
    )
    parser.add_argument(
        "--run-pytest",
        action="store_true",
        help="Run the deterministic Pytest suite before generating the report.",
    )
    args = parser.parse_args()

    if args.run_pytest:
        run_pytest()

    report_path = generate_quality_report()
    print(f"Report generated: {report_path}")
