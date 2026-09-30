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
    The security rule we want is:
    After resolving the requested path, the file still must still be inside the repository directory.
    a real, deterministic path-traversal security test
    """
    repo_path = REPOSITORY_PATHS["demo-app"].resolve()
    secret_file = repo_path.parent / "secret.txt"

    try:
        secret_file.write_text("TOP SECRET")

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
        assert result.response["result"]["result"]["error"] == "Invalid file path."

    finally:
        if secret_file.exists():
            secret_file.unlink()


def test_edit_file_blocks_path_traversal():
    """
    test cannot edit a file that is out of the project repository, security check
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

        assert result.response["result"]["result"]["error"] == "Invalid file path."
        assert secret_file.read_text() == "ORIGINAL CONTENT"

    finally:
        if secret_file.exists():
            secret_file.unlink()