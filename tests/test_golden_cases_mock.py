"""
Tests that the golden evaluation cases can be loaded and
contain the expected fields and evaluation values.

These tests do not call the LLM and do not test whether
the judge makes the correct evaluation.
"""

import json
from pathlib import Path


def load_golden_cases():
    path = Path(__file__).parents[1] / "data" / "golden_cases.json"

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def test_golden_cases_are_valid():
    cases = load_golden_cases()

    assert len(cases) == 6

    for case in cases:
        assert "id" in case
        assert "ai_response" in case
        assert "expected_judge_evaluation" in case
        assert "description" in case

        assert case["expected_judge_evaluation"] in {"PASS", "FAIL"}
        assert isinstance(case["ai_response"], str)
        assert isinstance(case["description"], str)