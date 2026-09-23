from pathlib import Path

from src.reporting import generate_quality_report as generator
from src.reporting.models import PytestSummary, QualityReport
from src.reporting.serialization import load_quality_report, save_quality_report


FIXTURES = Path(__file__).parent / "fixtures"
PYTEST_FIXTURE = FIXTURES / "pytest_sample.xml"
DEEPEVAL_FIXTURE = FIXTURES / "deepeval_sample.json"


def configure_test_paths(monkeypatch, tmp_path):
    pytest_report = tmp_path / "pytest" / "junit.xml"
    deepeval_report_dir = tmp_path / "deepeval"
    summary_dir = tmp_path / "summary"
    history_dir = summary_dir / "history"
    output_report = summary_dir / "ai_quality_report.md"

    pytest_report.parent.mkdir(parents=True)
    deepeval_report_dir.mkdir(parents=True)
    history_dir.mkdir(parents=True)

    pytest_report.write_text(
        PYTEST_FIXTURE.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    deepeval_report = (
        deepeval_report_dir / "test_run_20260923_120000.json"
    )

    deepeval_report.write_text(
        DEEPEVAL_FIXTURE.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        generator,
        "PYTEST_REPORT",
        pytest_report,
    )
    monkeypatch.setattr(
        generator,
        "DEEPEVAL_REPORT_DIR",
        deepeval_report_dir,
    )
    monkeypatch.setattr(
        generator,
        "SUMMARY_DIR",
        summary_dir,
    )
    monkeypatch.setattr(
        generator,
        "HISTORY_DIR",
        history_dir,
    )
    monkeypatch.setattr(
        generator,
        "OUTPUT_REPORT",
        output_report,
    )

    return history_dir, output_report


def test_generate_quality_report_first_run(
    monkeypatch,
    tmp_path,
):
    history_dir, output_report = configure_test_paths(
        monkeypatch,
        tmp_path,
    )

    report_path = generator.generate_quality_report()

    assert report_path == output_report
    assert output_report.exists()

    history_files = list(history_dir.glob("*.json"))

    assert len(history_files) == 1

    saved_report = load_quality_report(history_files[0])

    assert saved_report.run_id.startswith("run_")
    assert saved_report.pytest is not None
    assert saved_report.pytest.total == 5
    assert saved_report.pytest.passed == 3
    assert saved_report.pytest.failed == 1

    assert len(saved_report.deepeval) == 1
    assert saved_report.comparison is None

    markdown = output_report.read_text(encoding="utf-8")

    assert "# AI Quality Report" in markdown
    assert "## Pytest" in markdown
    assert "## DeepEval" in markdown
    assert "## Comparison With Previous Run" not in markdown


def test_generate_quality_report_compares_with_previous_run(
    monkeypatch,
    tmp_path,
):
    history_dir, output_report = configure_test_paths(
        monkeypatch,
        tmp_path,
    )

    previous_report = QualityReport(
        run_id="run_previous",
        timestamp="2026-09-22T10:00:00",
        pytest=PytestSummary(
            total=5,
            passed=2,
            failed=2,
            skipped=1,
            errors=0,
            duration_seconds=1.0,
        ),
    )

    previous_path = history_dir / "run_previous.json"

    save_quality_report(
        report=previous_report,
        output_path=previous_path,
    )

    generator.generate_quality_report()

    history_files = list(history_dir.glob("*.json"))

    assert len(history_files) == 2

    current_path = next(
        path
        for path in history_files
        if path.name != "run_previous.json"
    )

    current_report = load_quality_report(current_path)

    assert current_report.comparison is not None

    comparison = current_report.comparison

    assert comparison.previous_run_id == "run_previous"
    assert comparison.current_run_id == current_report.run_id

    assert comparison.pytest_changes["passed"] == 1
    assert comparison.pytest_changes["failed"] == -1

    assert output_report.exists()

    markdown = output_report.read_text(encoding="utf-8")

    assert "## Comparison With Previous Run" in markdown
    assert "run_previous" in markdown