from src.config import AGENT_MODEL
from src.providers.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, client, model=AGENT_MODEL):
        self.client = client
        self.model = model

    def generate(self, prompt, config=None):
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )

        return response