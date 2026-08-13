from src.metrics import calculate_accuracy
import pytest




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


def test_calculate_accuracy_empty_list():
    expected = ["PASS", "FAIL", "PASS", "FAIL"]
    actual = []

    with pytest.raises(ValueError):
        calculate_accuracy(expected, actual)




def test_calculate_accuracy_mismatched_lengths():
    expected = ["PASS", "FAIL", "PASS"]
    actual = ["PASS", "FAIL"]

    with pytest.raises(ValueError):
        calculate_accuracy(expected, actual)