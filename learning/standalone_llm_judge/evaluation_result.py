"""
Pydantic response model for the standalone LLM-as-a-judge learning example.

This model defines the structured result returned by the evaluator.
It is preserved as part of the project's earlier learning implementation
and is not used by the current DeepEval-based evaluation pipeline.
"""


from pydantic import BaseModel
from typing import Literal


class EvaluationResult(BaseModel):
    result: Literal["PASS", "FAIL"]
    behavior: Literal["answer", "ask_for_clarification"]
    answer: Literal["yes", "no"] | None
    reason: str