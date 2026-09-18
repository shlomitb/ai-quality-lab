from abc import ABC, abstractmethod


class LLMProvider(ABC):

    #Any LLM provider used by our application must have a generate() method.
    @abstractmethod
    def generate(self, prompt, config=None):
        pass

    def send_tool_results(self, tool_results, config=None):
        raise NotImplementedError