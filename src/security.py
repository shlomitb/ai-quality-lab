# src/security.py

SENSITIVE_FIELDS = {
    "internal_notes",
}



def sanitize_ticket(ticket: dict) -> dict:
    return {
        key: value
        for key, value in ticket.items()
        if key not in SENSITIVE_FIELDS
    }


def sanitize_tool_result(tool_name: str, result: dict) -> dict:
    if tool_name == "get_ticket":
        ticket = result.get("result")

        if isinstance(ticket, dict):
            return {
                **result,
                "result": sanitize_ticket(ticket),
            }

    return result