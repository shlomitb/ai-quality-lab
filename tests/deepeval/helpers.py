import os

from deepeval.models import GeminiModel


def create_gemini_model() -> GeminiModel:
    return GeminiModel(
        model="gemini-2.5-flash",
        api_key=os.environ["GEMINI_API_KEY"],
        temperature=0,
    )