from pydantic import BaseModel
from typing import Literal


class EvaluationResult(BaseModel):
    result: Literal["PASS", "FAIL"]
    behavior: Literal["answer", "ask_for_clarification"]
    answer: Literal["yes", "no"] | None
    reason: str