from unittest.mock import Mock
from src.evaluator import evaluate_response
from src.evaluation_result import EvaluationResult


"""
This test file calls the LLM evaluator without calling Gemini.

They test that evaluate_response() handles the LLM's result correctly.

It does not test whether Gemini itself is a good judge.
"""

def test_evaluator_returns_pass():
    client = Mock()

    client.models.generate_content.return_value.parsed = EvaluationResult(
        result="PASS",
        behavior="answer",
        answer="yes",
        reason="The AI correctly stated that an unopened product can be returned within 30 days."
    )

    result = evaluate_response(
        client=client,
        policy="Customers may return unopened products within 30 days.",
        question="Can I return an unopened product after 20 days?",
        ai_response="Yes, you can return it.",
        evaluation_criteria=(
            "The AI should state that an unopened product "
            "can be returned within 30 days."
        )
    )

    assert result.result == "PASS"


def test_evaluator_returns_fail():
    client = Mock()


    client.models.generate_content.return_value.parsed = EvaluationResult(
        result="FAIL",
        behavior="answer",
        answer="no",
        reason="The AI correctly stated that an unopened product can be returned within 30 days."
    )

    result = evaluate_response(
        client=client,
        policy="Customers may return unopened products within 30 days.",
        question="Can I return an unopened product after 20 days?",
        ai_response="No, unopened products cannot be returned.",
        evaluation_criteria=(
            "The AI should state that an unopened product "
            "can be returned within 30 days."
        )
    )

    assert result.result == "FAIL"


def test_evaluator_calls_llm():
    client = Mock()

    client.models.generate_content.return_value.parsed = EvaluationResult(
        result="PASS",
        behavior="answer",
        answer="yes",
        reason="The AI correctly stated that an unopened product can be returned within 30 days."
    )

    question = "Can I return an unopened product after 20 days?"
    ai_response = "Yes, you can return it."
    criteria = (
        "The AI should state that an unopened product "
        "can be returned within 30 days."
    )
    policy = "Customers may return unopened products within 30 days."

    evaluate_response(
        client=client,
        policy=policy,
        question=question,
        ai_response=ai_response,
        evaluation_criteria=criteria
    )

    client.models.generate_content.assert_called_once()