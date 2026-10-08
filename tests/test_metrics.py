import pytest
from src.metrics import (
    answer_accuracy,
    behavior_accuracy,
    calculate_accuracy,
    judge_accuracy
)



def test_calculate_accuracy_all_correct():
    expected = ["PASS", "FAIL", "PASS", "FAIL"]
    actual = ["PASS", "FAIL", "PASS", "FAIL"]

    result = calculate_accuracy(expected, actual)

    assert result == 1.0


def test_calculate_accuracy_with_mismatch():
    expected = ["PASS", "FAIL", "PASS", "FAIL"]
    actual = ["PASS", "PASS", "PASS", "FAIL"]

    result = calculate_accuracy(expected, actual)

    assert result == 0.75


def test_calculate_accuracy_all_wrong():
    expected = ["PASS", "FAIL", "PASS", "FAIL"]
    actual = ["FAIL", "PASS", "FAIL", "PASS"]

    result = calculate_accuracy(expected, actual)

    assert result == 0.0


def test_calculate_accuracy_empty_actual_list():
    expected = ["PASS", "FAIL", "PASS", "FAIL"]
    actual = []

    with pytest.raises(ValueError):
        calculate_accuracy(expected, actual)


def test_calculate_accuracy_mismatched_lengths():
    expected = ["PASS", "FAIL", "PASS"]
    actual = ["PASS", "FAIL"]

    with pytest.raises(ValueError):
        calculate_accuracy(expected, actual)


def test_behavior_accuracy():
    results = [
        {
            "expected_behavior": "PASS",
            "actual_behavior": "PASS",
        },
        {
            "expected_behavior": "FAIL",
            "actual_behavior": "PASS",
        },
        {
            "expected_behavior": "PASS",
            "actual_behavior": "PASS",
        },
    ]

    result = behavior_accuracy(results)

    assert result == 2 / 3


def test_answer_accuracy():
    results = [
        {
            "expected_answer": "yes",
            "actual_answer": "yes",
        },
        {
            "expected_answer": "no",
            "actual_answer": "yes",
        },
        {
            "expected_answer": "yes",
            "actual_answer": "yes",
        },
    ]

    result = answer_accuracy(results)

    assert result == 2 / 3


def test_judge_accuracy():
    results = [
        {
            "expected_judge": "PASS",
            "actual_judge": "PASS",
        },
        {
            "expected_judge": "FAIL",
            "actual_judge": "FAIL",
        },
        {
            "expected_judge": "FAIL",
            "actual_judge": "PASS",
        },
    ]

    result = judge_accuracy(results)

    assert result == 2 / 3


def test_calculate_accuracy_both_lists_empty():
    result = calculate_accuracy([], [])

    assert result == 0.0