from deepeval.metrics import ToolPermissionMetric
from deepeval.test_case import LLMTestCase, ToolCall


def test_tool_permission_allows_authorized_tools():
    test_case = LLMTestCase(
        input="Review the repository and run the tests.",
        actual_output="The tests were run.",
        tools_called=[
            ToolCall(name="search_files"),
            ToolCall(name="read_file"),
            ToolCall(name="run_tests"),
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
            ToolCall(name="search_files"),
            ToolCall(name="edit_file"),
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