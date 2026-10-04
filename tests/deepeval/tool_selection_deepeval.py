"""
DeepEval tool-selection tests.

Given a user request and a set of available tools, did the agent choose the appropriate tools?

These tests evaluate whether the agent selects the appropriate tool when multiple tools are available.

They specifically test tool selection, not tool arguments, task completion, or step efficiency.
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
    Did the agent select the right tools

    The agent generates the actual tool calls.
    DeepEval then uses ToolCorrectnessMetric to evaluate whether the selected tools were appropriate given the available tools.

    The expected trajectory is:
        search_files
             ↓
        read_file

    And by using: should_consider_ordering=True
        Checking that the tools are used in this correct order.
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

    Since the question explicitly provides the file path, there is no reason for the LLM to call search_files first.

    Important: This test fails - chatGPT said for now o leave the test failing. Do not change the test.

    The test is doing its job. It says:
        Given that the user explicitly provides src/login.py, the agent should select only read_file.
        But the actual agent selected read_file plus unnecessary tools.
    The failure is therefore telling us about a real behavior problem in the agent.
    Expected:
        read_file

    Actual:
        read_file
        search_files
        search_files
        read_file
        request_tool_access
        run_tests

    DeepEval scored it only 0.25, because although read_file was correct, the additional tool choices were inappropriate.

    Keep this test as-is.
    Look at the agent's behavior/prompt to understand why it continues making unnecessary calls after successfully reading the known file.
    Decide whether this is something we want to fix in the agent itself.
    Re-run the test.
    Ideally get it back to 1.0.

    This is actually a useful discovery from our evaluation work.
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