from src.config import AGENT_MODEL, AGENT_PROVIDER
from src.providers.gemini import GeminiProvider


def create_provider(client, model=AGENT_MODEL):
    if AGENT_PROVIDER == "gemini":
        return GeminiProvider(
            client=client,
            model=model,
        )

    raise ValueError(
        f"Unsupported LLM provider: {AGENT_PROVIDER}"
    )


def ask_llm(
    client,
    prompt,
    model=AGENT_MODEL,
    config=None,
):
    provider = create_provider(
        client=client,
        model=model,
    )

    return provider.generate(
        prompt=prompt,
        config=config,
    )