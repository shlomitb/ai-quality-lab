from src.providers.base import LLMProvider
from src.providers.gemini import GeminiProvider
from src.llm import create_provider
from src.providers.response import AgentResponse, ToolCall, ToolResult


def test_gemini_provider_implements_llm_provider():
    assert issubclass(GeminiProvider, LLMProvider)





def test_agent_response_can_store_tool_calls_and_results():
    response = AgentResponse(
        final_text="The tests passed.",
        tool_calls=[
            ToolCall(
                name="run_tests",
                args={"repository_name": "demo-app"},
            )
        ],
        tool_results=[
            ToolResult(
                name="run_tests",
                response={
                    "result": {
                        "status": "passed"
                    }
                },
            )
        ],
    )

    assert response.final_text == "The tests passed."
    assert response.tool_calls[0].name == "run_tests"
    assert response.tool_calls[0].args["repository_name"] == "demo-app"
    assert response.tool_results[0].name == "run_tests"
    assert response.tool_results[0].response["result"]["status"] == "passed"


def test_create_provider_returns_gemini_provider():
    provider = create_provider(client=None)

    assert isinstance(provider, GeminiProvider)