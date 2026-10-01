"""
Deterministic, non-llm tests, that test the agent’s skill-selection logic to ensure user requests are routed
to the correct skill based on keywords, while handling ambiguous, unmatched, and case-insensitive requests correctly.

Run with: python -m pytest tests\test_skill_routing.py -q
"""


import pytest

from src.skills import select_skill


@pytest.mark.parametrize(
    "question, expected_skill",
    [
        (
            "Investigate BUG-123 and determine the cause.",
            "investigate-bug",
        ),
        (
            "Please review this code for maintainability.",
            "review-code",
        ),
        (
            "Review this code and run the tests to verify your findings.",
            "review-code",
        ),
        (
            "Investigate BUG-456 and fix the failing test.",
            "investigate-bug",
        ),
    ],
)

def test_select_skill(question, expected_skill):
    assert select_skill(question) == expected_skill


def test_select_skill_returns_no_skill_for_ambiguous_request():
    question = "Please review this bug."

    assert select_skill(question) == ""


def test_select_skill_returns_no_skill_for_unrelated_request():
    question = "What is the weather today?"

    assert select_skill(question) == ""


def test_select_skill_is_case_insensitive():
    question = "INVESTIGATE BUG-123 AND FIX THE FAILURE."

    assert select_skill(question) == "investigate-bug"