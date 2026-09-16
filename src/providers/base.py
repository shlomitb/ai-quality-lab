from abc import ABC, abstractmethod


class LLMProvider(ABC):

    #Any LLM provider used by our application must have a generate() method.
    @abstractmethod
    def generate(self, prompt, config=None):
        pass