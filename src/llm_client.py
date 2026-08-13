import os

from dotenv import load_dotenv
from google import genai


def create_client():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY was not found.")

    return genai.Client(api_key=api_key)


def call_llm(client, model, prompt, config=None):
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=config
    )

    return response