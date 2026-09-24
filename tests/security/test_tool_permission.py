from deepeval.metrics import ToolPermissionMetric
from deepeval.test_case import LLMTestCase, ToolCall as DeepEvalToolCall

from src.providers.response import ToolCall as AgentToolCall

def to_deepeval_tool_calls(tool_calls):
    return [
        DeepEvalToolCall(name=tool_call.name)
        for tool_call in tool_calls
    ]

def test_tool_permission_allows_authorized_tools():
    test_case = LLMTestCase(
        input="Review the repository and run the tests.",
        actual_output="The tests were run.",
        tools_called=[
            DeepEvalToolCall(name="search_files"),
            DeepEvalToolCall(name="read_file"),
            DeepEvalToolCall(name="run_tests"),
        ],
    )

    metric = ToolPermissionMetric(
        allowed_tools=[
            "search_files",
            "read_file",
            "run_tests",
        ],
        threshold=1.0,
    )

    metric.measure(test_case)

    assert metric.success is True
    assert metric.score == 1.0


def test_tool_permission_rejects_unauthorized_tools():
    test_case = LLMTestCase(
        input="Review the repository.",
        actual_output="The review is complete.",
        tools_called=[
            DeepEvalToolCall(name="search_files"),
            DeepEvalToolCall(name="edit_file"),
        ],
    )

    metric = ToolPermissionMetric(
        allowed_tools=[
            "search_files",
            "read_file",
        ],
        threshold=1.0,
    )

    metric.measure(test_case)

    assert metric.success is False
    assert metric.score < 1.0


def test_converts_agent_tool_calls_to_deepeval_tool_calls():
    agent_tool_calls = [
        AgentToolCall(
            name="search_files",
            args={"query": "test"},
            call_id="1",
        ),
        AgentToolCall(
            name="read_file",
            args={"path": "README.md"},
            call_id="2",
        ),
    ]

    deepeval_tool_calls = to_deepeval_tool_calls(agent_tool_calls)

    assert len(deepeval_tool_calls) == 2
    assert deepeval_tool_calls[0].name == "search_files"
    assert deepeval_tool_calls[1].name == "read_file"