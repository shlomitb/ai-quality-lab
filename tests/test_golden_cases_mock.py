
import json
from unittest.mock import Mock
from src.evaluation_result import EvaluationResult

from src.evaluator import evaluate_response


def load_golden_cases():
    with open("data/golden_cases.json", "r") as file:
        return json.load(file)


def test_mock_golden_cases():
    """
    Verifies that your Python code correctly handles the judge's result.
    But it doesn't test the judge.
    """

    cases = load_golden_cases()

    for case in cases:
        client = Mock()

        # Pretend the LLM judge returned the expected result.

        client.models.generate_content.return_value.parsed = EvaluationResult(
            result=case["expected_judge_evaluation"],
            behavior="answer",
            answer="yes",
            reason="Mocked judge response."
        )

        result = evaluate_response(
            client=client,
            policy=(
                "Customers may return unopened products within 30 days.\n"
                "Opened products may be returned within 14 days "
                "only if they are defective.\n"
                "Digital products cannot be returned.\n"
                "Refunds are issued to the original payment method."
            ),
            question="Can I return an unopened product after 20 days?",
            ai_response=case["ai_response"],
            evaluation_criteria=(
                "The AI should state that an unopened product purchased "
                "20 days ago can be returned because unopened products "
                "can be returned within 30 days."
            )
        )

        assert isinstance(result, EvaluationResult)
        assert result.result == case["expected_judge_evaluation"]
