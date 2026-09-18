
from src.tools import (
    get_ticket,
    get_repository,
    search_files,
    run_tests,
    edit_file,
    read_file,
)


def request_tool_escalation(tool_name: str) -> dict:
    """
    Request access to an additional tool.

    The application must authorize the request before the tool
    becomes available.
    """
    return {
        "requested_tool": tool_name,
    }


TOOLS = {
    "get_ticket": get_ticket,
    "get_repository": get_repository,
    "search_files": search_files,
    "run_tests": run_tests,
    "edit_file": edit_file,
    "read_file": read_file,
    "request_tool_escalation": request_tool_escalation,
}


TOOL_DESCRIPTIONS = {
    "get_ticket": """
    Use this to retrieve information about a specific ticket.
    It requires the ticket_id argument.
    """,

    "get_repository": """
    Use this to retrieve information about a specific repository.
    It requires the repository_name argument.
    """,

    "search_files": """
    Use this to search files in a repository for a specific term.
    It requires the repository_name and search_term arguments.
    """,

    "run_tests": """
    Use this to run the test suite for a repository.
    It requires the repository_name argument.
    """,

    "edit_file": """
    Use this to modify the contents of an existing file in a repository.
    It requires the repository_name, file_path, and new_content arguments.
    """,

    "read_file": """
    Use this to read the contents of a specific file in a repository.
    It requires the repository_name and file_path arguments.
    """,

    "request_tool_escalation": """
    Request access to an additional tool when the currently available
    tools are insufficient.

    The application will check whether the requested tool is authorized.
    Do not assume the request will be approved.
    It requires the tool_name argument.
    """,
}


def get_tools(tool_names: list[str]) -> list:
    return [
        TOOLS[name]
        for name in tool_names
        if name in TOOLS
    ]


def get_tool_descriptions(tool_names: list[str]) -> str:
    descriptions = []

    for tool_name in tool_names:
        description = TOOL_DESCRIPTIONS.get(tool_name)

        if description:
            descriptions.append(
                f"- {tool_name}:\n{description.strip()}"
            )

    return "\n\n".join(descriptions)
