from google.genai import types
from src.config import AGENT_MODEL
from src.providers.base import LLMProvider
from src.providers.response import AgentResponse, ToolCall, ToolResult


class GeminiProvider(LLMProvider):
    def __init__(self, client, model=AGENT_MODEL):
        self.client = client
        self.model = model
        self.conversation = []

    def generate(self, prompt, config=None):
        user_content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=[user_content],
            config=config,
        )

        candidates = getattr(response, "candidates", None)

        if isinstance(candidates, list) and candidates:
            self.conversation = [
                user_content,
                candidates[0].content,
            ]
        else:
            self.conversation = [
                user_content,
            ]

        tool_calls = []

        function_calls = getattr(response, "function_calls", None)

        if isinstance(function_calls, list):
            for function_call in function_calls:
                tool_calls.append(
                    ToolCall(
                        name=function_call.name,
                        args=dict(function_call.args or {}),
                        call_id=getattr(function_call, "id", None),
                    )
                )

        return AgentResponse(
            final_text=response.text or "",
            tool_calls=tool_calls,
            tool_results=[],
            parsed=response.parsed,
        )

    def send_tool_results(self, tool_results, config=None):
        function_response_parts = []

        for tool_result in tool_results:
            function_response_parts.append(
                types.Part.from_function_response(
                    name=tool_result.name,
                    response=tool_result.response,
                )
            )

        function_response_content = types.Content(
            role="tool",
            parts=function_response_parts,
        )

        self.conversation.append(function_response_content)

        response = self.client.models.generate_content(
            model=self.model,
            contents=list(self.conversation),
            config=config,
        )

        tool_calls = []

        for function_call in response.function_calls or []:
            tool_calls.append(
                ToolCall(
                    name=function_call.name,
                    args=dict(function_call.args or {}),
                    call_id=getattr(function_call, "id", None),
                )
            )

        self.conversation.append(
            response.candidates[0].content
        )

        return AgentResponse(
            final_text=response.text or "",
            tool_calls=tool_calls,
            tool_results=[],
            parsed=response.parsed,
        )