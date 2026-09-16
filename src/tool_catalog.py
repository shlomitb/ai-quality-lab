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
}


def get_tool_descriptions(tool_names: list[str]) -> str:
    descriptions = []

    for tool_name in tool_names:
        description = TOOL_DESCRIPTIONS.get(tool_name)

        if description:
            descriptions.append(
                f"- {tool_name}:\n{description.strip()}"
            )

    return "\n\n".join(descriptions)


get_tool_descriptions(
    ["search_files", "read_file"]
)