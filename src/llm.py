from src.config import AGENT_MODEL
from src.providers.gemini import GeminiProvider


def ask_llm(
    client,
    prompt,
    model=AGENT_MODEL,
    config=None,
):
    provider = GeminiProvider(
        client=client,
        model=model,
    )

    return provider.generate(
        prompt=prompt,
        config=config,
    )