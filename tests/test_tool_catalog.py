from src.skills import get_selected_skill
from src.tool_catalog import get_tools, get_tool_descriptions, TOOLS, TOOL_DESCRIPTIONS


def test_bug_tool_descriptions_include_expected_tools():
    descriptions = get_tool_descriptions(
        [
            "get_ticket",
            "run_tests",
            "read_file",
            "edit_file",
        ]
    )

    assert "get_ticket" in descriptions
    assert "run_tests" in descriptions
    assert "read_file" in descriptions
    assert "edit_file" in descriptions

    assert "search_files" not in descriptions
    assert "get_repository" not in descriptions


def test_review_tool_descriptions_include_expected_tools():
    descriptions = get_tool_descriptions(
        [
            "search_files",
            "read_file",
        ]
    )

    assert "search_files" in descriptions
    assert "read_file" in descriptions

    assert "run_tests" not in descriptions
    assert "edit_file" not in descriptions


def test_bug_skill_gets_only_bug_tools():
    tools = get_tools(
        [
            "get_ticket",
            "run_tests",
            "read_file",
            "edit_file",
        ]
    )

    tool_names = [tool.__name__ for tool in tools]

    assert tool_names == [
        "get_ticket",
        "run_tests",
        "read_file",
        "edit_file",
    ]


def test_review_skill_gets_only_review_tools():
    tools = get_tools(
        [
            "search_files",
            "read_file",
        ]
    )

    tool_names = [tool.__name__ for tool in tools]

    assert tool_names == [
        "search_files",
        "read_file",
    ]


def test_bug_skill_tools_are_correct():
    skill = get_selected_skill(
        "Please investigate BUG-456 and fix the failing test."
    )

    assert skill is not None
    assert skill.tools == [
        "get_ticket",
        "run_tests",
        "read_file",
        "edit_file",
    ]


def test_review_skill_tools_are_correct():
    skill = get_selected_skill(
        "Please review this code for maintainability."
    )

    assert skill is not None
    assert skill.tools == [
        "search_files",
        "read_file",
    ]


def test_request_tool_access_is_available():
    tools = get_tools(["request_tool_access"])

    assert len(tools) == 1
    assert tools[0].__name__ == "request_tool_access"


def test_every_registered_tool_has_a_description():
    missing_descriptions = [
        tool_name
        for tool_name in TOOLS
        if tool_name not in TOOL_DESCRIPTIONS
        or not TOOL_DESCRIPTIONS[tool_name].strip()
    ]

    assert not missing_descriptions, (
        f"Missing descriptions for registered tools: "
        f"{missing_descriptions}"
    )


def test_get_tools_ignores_unknown_tool_names():
    tools = get_tools(
        [
            "get_ticket",
            "does_not_exist",
            "read_file",
        ]
    )

    tool_names = [tool.__name__ for tool in tools]

    assert tool_names == [
        "get_ticket",
        "read_file",
    ]