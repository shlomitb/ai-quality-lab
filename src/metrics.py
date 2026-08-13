def calculate_accuracy(expected, actual):

    if len(expected) != len(actual):
        raise ValueError("Expected and actual results must have the same length.")

    if not expected:
        return 0.0

    correct = 0

    for expected_value, actual_value in zip(expected, actual):
        if expected_value == actual_value:
            correct += 1

    return correct / len(expected)


def behavior_accuracy(results):
    expected = [result["expected_behavior"] for result in results]
    actual = [result["actual_behavior"] for result in results]

    return calculate_accuracy(expected, actual)


def answer_accuracy(results):
    expected = [result["expected_answer"] for result in results]
    actual = [result["actual_answer"] for result in results]

    return calculate_accuracy(expected, actual)


def judge_accuracy(results):
    expected = [result["expected_judge"] for result in results]
    actual = [result["actual_judge"] for result in results]

    return calculate_accuracy(expected, actual)