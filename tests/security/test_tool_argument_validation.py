"""
Tests security protections against unsafe tool arguments,
including path-traversal attempts that could access or modify files outside the repository.
"""
from src.agent import execute_tool_call
from src.providers.response import ToolCall
from src.skills import SelectedSkill
from src.tools import (
    REPOSITORY_PATHS,
    edit_file,
    read_file,
)


def test_read_file_blocks_path_traversal():
    """
    read_file must reject a path that resolves outside the repository.
    The external file must never be returned to the agent.
    """
    repo_path = REPOSITORY_PATHS["demo-app"].resolve()
    secret_file = repo_path.parent / "secret.txt"

    try:
        secret_file.write_text("TOP SECRET", encoding="utf-8")

        selected_skill = SelectedSkill(
            name="review-code",
            instructions="",
            tools=["read_file"],
        )

        tool_call = ToolCall(
            name="read_file",
            args={
                "repository_name": "demo-app",
                "file_path": "../secret.txt",
            },
            call_id="test-path-traversal",
        )

        result = execute_tool_call(
            tool_call=tool_call,
            available_tools=[read_file],
            selected_skill=selected_skill,
        )

        assert result.response["result"]["error"] == "Invalid file path."
        assert "TOP SECRET" not in str(result.response)

    finally:
        if secret_file.exists():
            secret_file.unlink()


def test_edit_file_blocks_path_traversal():
    """
    edit_file must reject paths outside the repository and must not
    modify the external file.
    """
    repo_path = REPOSITORY_PATHS["demo-app"].resolve()
    secret_file = repo_path.parent / "secret.txt"

    try:
        secret_file.write_text("ORIGINAL CONTENT")

        selected_skill = SelectedSkill(
            name="investigate-bug",
            instructions="",
            tools=["edit_file"],
        )

        tool_call = ToolCall(
            name="edit_file",
            args={
                "repository_name": "demo-app",
                "file_path": "../secret.txt",
                "new_content": "MALICIOUS CHANGE",
            },
            call_id="test-edit-path-traversal",
        )

        result = execute_tool_call(
            tool_call=tool_call,
            available_tools=[edit_file],
            selected_skill=selected_skill,
        )

        assert result.response["result"]["error"] == "Invalid file path."
        assert secret_file.read_text() == "ORIGINAL CONTENT"

    finally:
        if secret_file.exists():
            secret_file.unlink()


def test_read_file_allows_normalized_path_inside_repository():
    """
    A path containing '..' is allowed when the resolved path remains
    inside the repository.
    """
    selected_skill = SelectedSkill(
        name="review-code",
        instructions="",
        tools=["read_file"],
    )

    tool_call = ToolCall(
        name="read_file",
        args={
            "repository_name": "demo-app",
            "file_path": "src/../src/login.py",
        },
        call_id="test-normalized-path",
    )

    result = execute_tool_call(
        tool_call=tool_call,
        available_tools=[read_file],
        selected_skill=selected_skill,
    )

    assert "error" not in result.response["result"]
    assert result.response["result"]["file_path"] == "src/../src/login.py"



def test_read_file_blocks_deep_path_traversal():
    """
    read_file must reject paths that traverse multiple levels
    outside the repository.
    """
    repo_path = REPOSITORY_PATHS["demo-app"].resolve()
    secret_file = repo_path.parent.parent / "secret.txt"

    try:
        secret_file.write_text("TOP SECRET", encoding="utf-8")

        selected_skill = SelectedSkill(
            name="review-code",
            instructions="",
            tools=["read_file"],
        )

        tool_call = ToolCall(
            name="read_file",
            args={
                "repository_name": "demo-app",
                "file_path": "../../secret.txt",
            },
            call_id="test-deep-path-traversal",
        )

        result = execute_tool_call(
            tool_call=tool_call,
            available_tools=[read_file],
            selected_skill=selected_skill,
        )

        assert result.response["result"]["error"] == "Invalid file path."
        assert "TOP SECRET" not in str(result.response)

    finally:
        if secret_file.exists():
            secret_file.unlink()