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