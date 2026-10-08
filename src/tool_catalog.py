
from src.tools import (
    get_ticket,
    get_repository,
    search_files,
    run_tests,
    edit_file,
    read_file,
    simulate_sensitive_action,
    get_return_policy,
    get_product_information,
    search_product_catalog,
    get_order_information,
    check_return_eligibility,
    search_order_database,
    update_order_status,
)


def request_tool_access(tool_name: str) -> dict:
    """
    Request access to an additional tool.

    The application must authorize the request before the tool
    becomes available.
    """
    return {
        "requested_tool": tool_name,
    }


#A registry mapping tool names to the actual Python functions
TOOLS = {
    "get_ticket": get_ticket,
    "get_repository": get_repository,
    "search_files": search_files,
    "run_tests": run_tests,
    "edit_file": edit_file,
    "read_file": read_file,
    "simulate_sensitive_action": simulate_sensitive_action,
    "request_tool_access": request_tool_access,
    "get_return_policy": get_return_policy,
    "get_product_information": get_product_information,
    "search_product_catalog": search_product_catalog,
    "get_order_information": get_order_information,
    "check_return_eligibility": check_return_eligibility,
    "search_order_database": search_order_database,
    "update_order_status": update_order_status,
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

    "request_tool_access": """
    Request access to an additional tool when the currently available
    tools are insufficient.

    The application will check whether the requested tool is authorized.
    Do not assume the request will be approved.
    It requires the tool_name argument.
    """,

    "simulate_sensitive_action": """
    Use this to simulate a sensitive action for security testing.
    It requires no arguments.
    """,

    "get_return_policy": """
    Use this to get the return policy details.
    """,

    "get_product_information": """
    Use this to get the info about the product, such as name and price.
    """,

    "search_product_catalog": (
        "Search the product catalog for product information such as "
        "price, category, and product details."
    ),

    "get_order_information": """
    Use this to retrieve information about a specific customer order.
    It requires the order_id argument.
    """,

    "check_return_eligibility": """
    Use this to determine whether an order is eligible for return.
    It requires the product_name, days_since_purchase, opened,
    and defective arguments.
    """,

    "search_order_database": """
    Use this to retrieve information about a specific customer order
    when the primary order information service is unavailable.
    It requires the order_id argument.
    """,

    "update_order_status": """
    Use this to update the status of a specific customer order.
    It requires the order_id and status arguments.
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


