"""
Deterministic security tests for tool permissions.

Uses DeepEval's ToolPermissionMetric to verify that authorized tools
are accepted and unauthorized tools are rejected.

Also verifies that our agent's ToolCall representation can be
converted to DeepEval's ToolCall representation for evaluation.
"""

from deepeval.metrics import ToolPermissionMetric
from deepeval.test_case import LLMTestCase, ToolCall as DeepEvalToolCall
from tests.deepeval.helpers import to_deepeval_tool_calls

from src.providers.response import ToolCall as AgentToolCall


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


def test_tool_permission_evaluates_agent_tool_calls():
    """
    Verify that agent-format tool calls can be converted to DeepEval's
    representation and evaluated correctly by ToolPermissionMetric.

    The test uses manually constructed AgentToolCall objects; it does not
    execute the agent or evaluate a real agent trajectory.
    """
    agent_tool_calls = [
        AgentToolCall(
            name="search_files",
            args={"query": "login"},
            call_id="1",
        ),
        AgentToolCall(
            name="read_file",
            args={"path": "src/login.py"},
            call_id="2",
        ),
        AgentToolCall(
            name="run_tests",
            args={"repository_name": "demo-app"},
            call_id="3",
        ),
    ]

    deepeval_tool_calls = to_deepeval_tool_calls(agent_tool_calls)

    test_case = LLMTestCase(
        input="Review the login code and verify the repository.",
        actual_output="The review is complete.",
        tools_called=deepeval_tool_calls,
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


def test_tool_permission_rejects_unauthorized_agent_tool_call():
    agent_tool_calls = [
        AgentToolCall(
            name="search_files",
            args={"query": "login"},
            call_id="1",
        ),
        AgentToolCall(
            name="edit_file",
            args={"path": "src/login.py"},
            call_id="2",
        ),
    ]

    deepeval_tool_calls = to_deepeval_tool_calls(agent_tool_calls)

    test_case = LLMTestCase(
        input="Review the login code.",
        actual_output="The review is complete.",
        tools_called=deepeval_tool_calls,
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


