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


def redact_sensitive_values(value):
    if isinstance(value, str):
        for pattern, replacement in SENSITIVE_VALUE_PATTERNS:
            value = pattern.sub(replacement, value)
        return value

    if isinstance(value, dict):
        return {
            key: redact_sensitive_values(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            redact_sensitive_values(item)
            for item in value
        ]

    return value


def sanitize_ticket(ticket: dict) -> dict:
    sanitized = {
        key: value
        for key, value in ticket.items()
        if key not in SENSITIVE_FIELDS
    }

    return redact_sensitive_values(sanitized)


def sanitize_tool_result(tool_name: str, result: dict) -> dict:
    if tool_name == "get_ticket":
        ticket = result.get("result")

        if isinstance(ticket, dict):
            return {
                **result,
                "result": sanitize_ticket(ticket),
            }

    return result


