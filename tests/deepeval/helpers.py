import os

from deepeval.models import GeminiModel
from deepeval.test_case import ToolCall as DeepEvalToolCall


def create_gemini_model() -> GeminiModel:
    return GeminiModel(
        model="gemini-2.5-flash",
        api_key=os.environ["GEMINI_API_KEY"],
        temperature=0,
    )


def to_deepeval_tool_calls(tool_calls):
    # Permission evaluation only needs the tool names.
    return [
        DeepEvalToolCall(name=tool_call.name)
        for tool_call in tool_calls
    ]