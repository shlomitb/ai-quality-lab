from src.providers.base import LLMProvider
from src.providers.gemini import GeminiProvider


def test_gemini_provider_implements_llm_provider():
    assert issubclass(GeminiProvider, LLMProvider)