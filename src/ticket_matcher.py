import re
from typing import Any, Iterable

JIRA_PATTERN = re.compile(r"\b[A-Z][A-Z0-9]+-\d+\b", re.IGNORECASE)


def extract_tickets(value: Any) -> list[str]:
    if value is None:
        return []
    return list(dict.fromkeys(m.group(0).upper() for m in JIRA_PATTERN.finditer(str(value))))


def extract_one_ticket(values: Iterable[Any]) -> tuple[str | None, str | None]:
    found: list[str] = []
    for value in values:
        found.extend(extract_tickets(value))
    unique = list(dict.fromkeys(found))
    if not unique:
        return None, "Missing Jira Ticket"
    if len(unique) > 1:
        return None, "Multiple Jira Tickets Detected"
    return unique[0], None
