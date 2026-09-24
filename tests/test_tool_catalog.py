from src.tool_catalog import get_tool_descriptions


def test_bug_skill_gets_bug_tools():
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


def test_review_skill_gets_review_tools():
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


from src.tool_catalog import get_tools


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
    from src.skills import get_selected_skill

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
    from src.skills import get_selected_skill

    skill = get_selected_skill(
        "Please review this code for maintainability."
    )

    assert skill is not None
    assert skill.tools == [
        "search_files",
        "read_file",
    ]


def test_escalation_tool_is_available():
    from src.tool_catalog import get_tools

    tools = get_tools(["request_tool_access"])

    assert len(tools) == 1
    assert tools[0].__name__ == "request_tool_access"