from src.config import AGENT_MODEL
from src.providers.base import LLMProvider
from src.providers.response import AgentResponse, ToolCall, ToolResult


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

        tool_calls = []
        tool_results = []

        for content in response.automatic_function_calling_history or []:
            for part in content.parts or []:

                if part.function_call is not None:
                    tool_calls.append(
                        ToolCall(
                            name=part.function_call.name,
                            args=dict(part.function_call.args),
                        )
                    )

                function_response = getattr(
                    part,
                    "function_response",
                    None,
                )

                if function_response is not None:
                    tool_results.append(
                        ToolResult(
                            name=function_response.name,
                            response=dict(function_response.response),
                        )
                    )

        return AgentResponse(
            final_text=response.text or "",
            tool_calls=tool_calls,
            tool_results=tool_results,
        )