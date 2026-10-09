import os

from deepeval.models import GeminiModel
from deepeval.test_case import ToolCall as DeepEvalToolCall


def create_gemini_model(
    model_name: str = "gemini-2.5-flash",
) -> GeminiModel:
    """
    temperature=0: Low variability in how predictable or variable the model's responses are.
    The judge is encouraged to choose the most likely response. Good when you want more consistent evaluation results.
    """
    return GeminiModel(
        model=model_name,
        api_key=os.environ["GEMINI_API_KEY"],
        temperature=0,
    )


def to_deepeval_tool_calls(tool_calls) -> list[DeepEvalToolCall]:
    # Permission evaluation only needs the tool names.
    return [
        DeepEvalToolCall(name=tool_call.name)
        for tool_call in tool_calls
    ]