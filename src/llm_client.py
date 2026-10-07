import os

from dotenv import load_dotenv
from google import genai




class LLMConfigurationError(Exception):
    """Raised when the LLM client cannot be configured."""


def create_client():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise LLMConfigurationError(
            "LLM credentials were not configured."
        )

    return genai.Client(api_key=api_key)


def ask_llm(client, prompt, model="gemini-3.6-flash", config=None):
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=config
    )

    return response