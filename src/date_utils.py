from datetime import date, datetime
from typing import Any


FORMATS = ("%d-%m-%Y", "%d-%b-%y", "%d-%b-%Y", "%Y-%m-%d")


def parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def month_key(value: date) -> str:
    return value.strftime("%Y-%m")


def week_in_month(value: date) -> str:
    """Return Monday-Sunday week number, with the month-start partial week as W1."""
    first = value.replace(day=1)
    first_monday_offset = (7 - first.weekday()) % 7
    first_monday = first.toordinal() + first_monday_offset
    if value.toordinal() < first_monday:
        return "W1"
    return f"W{2 + (value.toordinal() - first_monday) // 7}"
