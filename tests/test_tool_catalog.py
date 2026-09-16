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