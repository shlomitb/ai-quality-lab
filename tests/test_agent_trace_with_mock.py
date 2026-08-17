from unittest.mock import Mock

from src.agent import get_tool_calls


"""

"""


def test_get_tool_calls():
    """
    Creating a fake version of the Gemini response structure
    The test does a fake Gemini response, where the llm call had 1 tool added.
    Checks that calling get_tool_calls() correctly extracts the given 1 tool name.

    content, part and function_call are all simulating the structure of the code in the response object passed into get_tool_calls(response)
    """
    response = Mock()

    function_call = Mock()
    function_call.name = "get_return_policy"

    part = Mock()
    part.function_call = function_call

    content = Mock()
    content.parts = [part]
    response.automatic_function_calling_history = [content]

    tool_calls = get_tool_calls(response)

    assert tool_calls == ["get_return_policy"]


def test_get_tool_calls_pass_no_tools():
    response = Mock()

    content = Mock()
    content.parts = []
    response.automatic_function_calling_history = [content]

    tool_calls = get_tool_calls(response)

    assert tool_calls == []


def test_get_tool_calls_with_two_tools():
    """
    Creating a fake version of the Gemini response structure:
    """
    response = Mock()

    function_call = Mock()
    function_call.name = "tool1"

    function_call2 = Mock()
    function_call2.name = "tool2"

    part = Mock()
    part.function_call = function_call

    part2 = Mock()
    part2.function_call = function_call2

    content = Mock()
    content.parts = [part, part2]
    response.automatic_function_calling_history = [content]

    tool_calls = get_tool_calls(response)

    assert tool_calls == ["tool1", "tool2"]