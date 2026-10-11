import json
from pathlib import Path

import pytest

from src.reporting.deepeval_report import load_deepeval_results


FIXTURE = (
    Path(__file__).parent
    / ".."
    / "fixtures"
    / "deepeval_sample.json"
)


def test_load_deepeval_results():
    results = load_deepeval_results(FIXTURE)

    assert len(results) == 1

    result = results[0]

    assert result.name == "test_dynamic_tool_access_agent"
    assert result.success is True

    assert result.trajectory == [
        "search_files",
        "read_file",
        "read_file",
        "request_tool_access(run_tests)",
        "run_tests",
    ]

    assert result.metrics[0].name == "Task Completion"
    assert result.metrics[0].score == 1.0
    assert result.metrics[0].threshold == 0.8

    assert result.metrics[1].name == "Step Efficiency"
    assert result.metrics[1].score == 1.0

    assert result.evaluation_cost == 0.0145


def test_load_deepeval_results_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_deepeval_results("does-not-exist.json")


def test_load_deepeval_results_invalid_json(tmp_path):
    report_file = tmp_path / "bad_report.json"

    report_file.write_text(
        "this is not valid JSON",
        encoding="utf-8",
    )

    with pytest.raises(json.JSONDecodeError):
        load_deepeval_results(report_file)


def test_load_deepeval_results_missing_test_cases(tmp_path):
    report_file = tmp_path / "missing_test_cases.json"

    report_file.write_text(
        '{"someOtherField": "value"}',
        encoding="utf-8",
    )

    results = load_deepeval_results(report_file)

    assert results == []


def test_load_deepeval_results_with_multiple_tests():
    fixture_path = (
        Path(__file__).resolve().parents[2]
        / "tests"
        / "fixtures"
        / "deepeval_multi_test.json"
    )

    results = load_deepeval_results(fixture_path)

    assert len(results) == 2

    first_test = results[0]

    assert first_test.name == (
        "test_bug_file_search_task_completion"
    )
    assert first_test.success is True
    assert first_test.trajectory == [
        "get_ticket",
        "request_tool_access(search_files)",
        "search_files",
    ]

    assert len(first_test.metrics) == 1
    assert first_test.metrics[0].name == "Task Completion"
    assert first_test.metrics[0].score == 1.0
    assert first_test.metrics[0].success is True

    second_test = results[1]

    assert second_test.name == (
        "test_dynamic_tool_access_agent"
    )
    assert second_test.success is False
    assert second_test.trajectory == [
        "get_ticket",
        "request_tool_access(run_tests)",
        "run_tests",
        "run_tests",
    ]

    assert len(second_test.metrics) == 2

    assert second_test.metrics[0].name == "Task Completion"
    assert second_test.metrics[0].success is True

    assert second_test.metrics[1].name == "Step Efficiency"
    assert second_test.metrics[1].score == 0.6
    assert second_test.metrics[1].threshold == 0.8
    assert second_test.metrics[1].success is False



def test_load_deepeval_results_extracts_execution_metrics(tmp_path):
    """
    Verifies that the duration comes from the trace timestamps, not runDuration.
    Verifies that two recorded tool calls produce a count of two.
    pytest.approx() avoids brittle floating-point comparisons.
    """
    report_file = tmp_path / "trace_report.json"

    report_data = {
        "testCases": [
            {
                "name": "test_agent_execution",
                "success": True,
                "actualOutput": "Done",
                "metricsData": [],
                "trace": {
                    "agentSpans": [
                        {
                            "startTime": "2026-10-09T07:46:49.098Z",
                            "endTime": "2026-10-09T07:46:58.989Z",
                            "toolsCalled": [
                                {
                                    "output": {"name": "search_files"}
                                },
                                {
                                    "output": {"name": "read_file"}
                                },
                            ],
                        }
                    ]
                },
            }
        ]
    }

    report_file.write_text(
        json.dumps(report_data),
        encoding="utf-8",
    )

    results = load_deepeval_results(report_file)

    assert len(results) == 1
    result = results[0]

    assert result.tool_call_count == 2
    assert result.trace_duration_seconds == pytest.approx(9.891)
    assert result.duration_seconds == pytest.approx(9.891)



def test_load_deepeval_results_without_timestamps(tmp_path):
    """
    Checks that missing timestamps don't cause an error and that the parser still captures the tool call.
    """
    report_file = tmp_path / "no_timestamps.json"

    report_data = {
        "testCases": [
            {
                "name": "test_agent_without_timestamps",
                "success": True,
                "actualOutput": "Done",
                "metricsData": [],
                "trace": {
                    "agentSpans": [
                        {
                            "toolsCalled": [
                                {
                                    "output": {"name": "search_files"}
                                }
                            ]
                        }
                    ]
                },
            }
        ]
    }

    report_file.write_text(
        json.dumps(report_data),
        encoding="utf-8",
    )

    results = load_deepeval_results(report_file)

    assert len(results) == 1
    assert results[0].tool_call_count == 1
    assert results[0].trace_duration_seconds is None
    assert results[0].duration_seconds is None



def test_load_deepeval_results_without_trace(tmp_path):
    """
    Checks that if a test result does not contain a trace field at all, then  the parser returns sensible defaults rather than fails.
    """
    report_file = tmp_path / "no_trace.json"

    report_data = {
        "testCases": [
            {
                "name": "test_agent_without_trace",
                "success": True,
                "actualOutput": "Done",
                "runDuration": 2.0,
                "metricsData": [],
            }
        ]
    }

    report_file.write_text(
        json.dumps(report_data),
        encoding="utf-8",
    )

    results = load_deepeval_results(report_file)

    assert len(results) == 1
    assert results[0].trajectory == []
    assert results[0].tool_call_count == 0
    assert results[0].trace_duration_seconds is None
