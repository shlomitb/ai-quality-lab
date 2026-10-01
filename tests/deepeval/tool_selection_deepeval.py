"""
DeepEval tool-selection tests.

These tests evaluate whether the agent selects the appropriate tool
when multiple tools are available.

They specifically test tool selection, not tool arguments,
task completion, or step efficiency.
Those dimensions are evaluated separately.


Run with (ex):
deepeval test run tests\deepeval\tool_selection_deepeval.py -k test_code_review_selects_search_files_when_file_is_unknown -v -s
"""

from dotenv import load_dotenv

from deepeval import assert_test
from deepeval.metrics import ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase, ToolCall

from src.agent import answer_customer_with_trace, get_tool_calls
from src.llm_client import create_client
from tests.deepeval.helpers import create_gemini_model


load_dotenv()

gemini_model = create_gemini_model()


def run_tool_selection_test(
    question: str,
    expected_tools: list[ToolCall],
    available_tools: list[ToolCall],
    threshold=0.5
):
    """
    Run one tool-selection evaluation.

    The agent generates the actual tool calls. DeepEval then uses
    ToolCorrectnessMetric to evaluate whether the selected tools
    were appropriate given the available tools.
    """
    client = create_client()

    response = answer_customer_with_trace(
        client=client,
        question=question,
    )

    print("\nAGENT TOOL CALLS:")
    print(response.tool_calls)

    print("\nEXTRACTED TOOL CALLS:")
    print(get_tool_calls(response))

    print("\nFINAL RESPONSE:")
    print(response.final_text)

    tools_called = [
        ToolCall(name=name)
        for name in get_tool_calls(response)
    ]

    test_case = LLMTestCase(
        input=question,
        actual_output=response.final_text,
        tools_called=tools_called,
        expected_tools=expected_tools,
    )

    metric = ToolCorrectnessMetric(
        threshold=threshold,
        model=gemini_model,
        available_tools=available_tools,
        should_consider_ordering=True,
    )

    assert_test(
        test_case=test_case,
        metrics=[metric],
    )


def test_code_review_searches_then_reads_when_file_is_unknown():
    """
    When the relevant file is unknown, the review-code skill should
    first use search_files to locate it and then use read_file to
    inspect the identified source file.
    """
    question = (
        "Review the login-related code in the demo-app repository "
        "and find the relevant source file that should be inspected."
    )

    run_tool_selection_test(
        question=question,
        expected_tools=[
            ToolCall(name="search_files"),
            ToolCall(name="read_file"),
        ],
        available_tools=[
            ToolCall(name="search_files"),
            ToolCall(name="read_file"),
        ]
    )


def test_code_review_selects_read_file_when_file_is_known():
    """
    When the repository and file path are already known,
    the review-code skill should use read_file rather than search_files.

    Since the question explicitly passes the file path, there is not reason for the llm to call search_files first
    """
    question = (
        "Review the code in the demo-app repository at src/login.py "
        "for potential bugs and maintainability problems."
    )

    run_tool_selection_test(
        question=question,
        expected_tools=[
            ToolCall(name="read_file"),
        ],
        available_tools=[
            ToolCall(name="search_files"),
            ToolCall(name="read_file"),
        ],
        threshold=1.0,
    )