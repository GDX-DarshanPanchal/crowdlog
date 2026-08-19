import re
from datetime import date


def action_summary(dates: list[date], memos: list[str], ticket: str) -> str:
    first = ", ".join(d.strftime("%m/%d") for d in sorted(set(dates)))
    cleaned: list[str] = []
    prefix = re.compile(rf"^\s*{re.escape(ticket)}\b[\s:;,_-]*", re.IGNORECASE)
    for memo in memos:
        text = " ".join(str(memo or "").split())
        text = prefix.sub("", text).strip(" -")
        if text and text not in cleaned:
            cleaned.append(text)
    return "\n".join([first, *[f"- {text}" for text in cleaned]])
