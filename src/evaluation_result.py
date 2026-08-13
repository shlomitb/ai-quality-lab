from pydantic import BaseModel
from typing import Literal


class EvaluationResult(BaseModel):
    result: Literal["PASS", "FAIL"]
    reason: str