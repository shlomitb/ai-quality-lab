"""
Tests the standalone LLM-as-a-judge evaluator.

These tests verify that evaluate_response() correctly handles
the structured result returned by the evaluator.

They do not call Gemini and do not test whether Gemini itself
is a good judge.
"""


from unittest.mock import Mock, patch

from learning.standalone_llm_judge.evaluator import evaluate_response
from learning.standalone_llm_judge.evaluation_result import EvaluationResult



def test_evaluator_returns_pass():
    client = Mock()

    expected_result = EvaluationResult(
        result="PASS",
        behavior="answer",
        answer="yes",
        reason=(
            "The AI correctly stated that an unopened product "
            "can be returned within 30 days."
        ),
    )

    mock_response = Mock()
    mock_response.parsed = expected_result

    with patch(
        "learning.standalone_llm_judge.evaluator.ask_llm",
        return_value=mock_response,
    ):
        result = evaluate_response(
            client=client,
            policy="Customers may return unopened products within 30 days.",
            question="Can I return an unopened product after 20 days?",
            ai_response="Yes, you can return it.",
            evaluation_criteria=(
                "The AI should state that an unopened product "
                "can be returned within 30 days."
            ),
        )

    assert result.result == "PASS"


def test_evaluator_returns_fail():
    client = Mock()

    expected_result = EvaluationResult(
        result="FAIL",
        behavior="answer",
        answer="no",
        reason=(
            "The AI incorrectly stated that an unopened product "
            "cannot be returned after 20 days."
        ),
    )

    mock_response = Mock()
    mock_response.parsed = expected_result

    with patch(
            "learning.standalone_llm_judge.evaluator.ask_llm",
            return_value=mock_response,
    ):
        result = evaluate_response(
            client=client,
            policy="Customers may return unopened products within 30 days.",
            question="Can I return an unopened product after 20 days?",
            ai_response="No, unopened products cannot be returned.",
            evaluation_criteria=(
                "The AI should state that an unopened product "
                "can be returned within 30 days."
            ),
        )

    assert result.result == "FAIL"


def test_evaluator_calls_ask_llm():
    client = Mock()

    expected_result = EvaluationResult(
        result="PASS",
        behavior="answer",
        answer="yes",
        reason="Mocked evaluator response.",
    )

    mock_response = Mock()
    mock_response.parsed = expected_result

    with patch(
            "learning.standalone_llm_judge.evaluator.ask_llm",
            return_value=mock_response,
    ) as mock_ask_llm:

        evaluate_response(
            client=client,
            policy="Customers may return unopened products within 30 days.",
            question="Can I return an unopened product after 20 days?",
            ai_response="Yes, you can return it.",
            evaluation_criteria=(
                "The AI should state that an unopened product "
                "can be returned within 30 days."
            ),
        )

    mock_ask_llm.assert_called_once()

