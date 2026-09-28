import re

SENSITIVE_FIELDS = {
    "internal_notes",
}

SENSITIVE_VALUE_PATTERNS = [
    (
        re.compile(r"(?i)(password\s*:\s*)\S+"),
        r"\1[REDACTED]",
    ),
]


def redact_sensitive_values(text: str) -> str:
    for pattern, replacement in SENSITIVE_VALUE_PATTERNS:
        text = pattern.sub(replacement, text)

    return text


def sanitize_ticket(ticket: dict) -> dict:
    sanitized = {}

    for key, value in ticket.items():
        if key in SENSITIVE_FIELDS:
            continue

        if isinstance(value, str):
            value = redact_sensitive_values(value)

        sanitized[key] = value

    return sanitized


def sanitize_tool_result(tool_name: str, result: dict) -> dict:
    if tool_name == "get_ticket":
        ticket = result.get("result")

        if isinstance(ticket, dict):
            return {
                **result,
                "result": sanitize_ticket(ticket),
            }

    return result


