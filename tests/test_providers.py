from src.providers.base import LLMProvider
from src.providers.gemini import GeminiProvider
from src.llm import create_provider
from src.providers.response import AgentResponse, ToolCall, ToolResult
from unittest.mock import Mock


def test_gemini_provider_implements_llm_provider():
    assert issubclass(GeminiProvider, LLMProvider)





def test_agent_response_can_store_tool_calls_and_results():
    response = AgentResponse(
        final_text="The tests passed.",
        tool_calls=[
            ToolCall(
                name="run_tests",
                args={"repository_name": "demo-app"},
                call_id="call-123",
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
                call_id="call-123",
            )
        ],
    )

    assert response.final_text == "The tests passed."
    assert response.tool_calls[0].name == "run_tests"
    assert response.tool_calls[0].args["repository_name"] == "demo-app"
    assert response.tool_results[0].name == "run_tests"
    assert response.tool_results[0].response["result"]["status"] == "passed"
    assert response.tool_calls[0].call_id == "call-123"
    assert response.tool_results[0].call_id == "call-123"

def test_create_provider_returns_gemini_provider():
    provider = create_provider(client=None)

    assert isinstance(provider, GeminiProvider)


def test_gemini_provider_extracts_function_calls():
    client = Mock()

    function_call = Mock()
    function_call.name = "get_return_policy"
    function_call.args = {
        "customer_type": "standard"
    }
    function_call.id = "call-123"

    response = Mock()
    response.function_calls = [function_call]
    response.text = ""
    response.parsed = None

    response_content = Mock()

    response.candidates = [
        Mock(content=response_content)
    ]

    client.models.generate_content.return_value = response

    provider = GeminiProvider(
        client=client,
        model="test-model",
    )

    result = provider.generate(
        prompt="test prompt",
        config=Mock(),
    )

    assert result.tool_calls == [
        ToolCall(
            name="get_return_policy",
            args={
                "customer_type": "standard"
            },
            call_id="call-123",
        )
    ]

    assert result.tool_results == []
    assert len(provider.conversation) == 2
    assert provider.conversation[1] is response_content


def test_gemini_provider_sends_tool_results_and_gets_next_response():
    client = Mock()

    first_response = Mock()
    first_response.text = ""
    first_response.parsed = None

    function_call = Mock()
    function_call.name = "run_tests"
    function_call.args = {
        "repository_name": "demo-app"
    }
    function_call.id = "call-123"

    first_response.function_calls = [function_call]

    first_model_content = Mock()
    first_response.candidates = [
        Mock(content=first_model_content)
    ]

    second_response = Mock()
    second_response.text = "The tests passed."
    second_response.parsed = None
    second_response.function_calls = []

    second_model_content = Mock()
    second_response.candidates = [
        Mock(content=second_model_content)
    ]

    client.models.generate_content.side_effect = [
        first_response,
        second_response,
    ]

    provider = GeminiProvider(
        client=client,
        model="test-model",
    )

    first_result = provider.generate(
        prompt="Run the tests.",
        config=Mock(),
    )

    assert first_result.tool_calls == [
        ToolCall(
            name="run_tests",
            args={
                "repository_name": "demo-app"
            },
            call_id="call-123",
        )
    ]

    tool_result = ToolResult(
        name="run_tests",
        response={
            "status": "passed"
        },
        call_id="call-123",
    )

    second_result = provider.send_tool_results(
        tool_results=[tool_result],
        config=Mock(),
    )

    assert second_result.final_text == "The tests passed."
    assert second_result.tool_calls == []
    assert second_result.tool_results == []

    assert client.models.generate_content.call_count == 2

    sent_contents = client.models.generate_content.call_args_list[1].kwargs[
        "contents"
    ]

    assert sent_contents[-1].role == "tool"
    assert sent_contents[-1].parts[0].function_response.name == "run_tests"