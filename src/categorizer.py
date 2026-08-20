from typing import Any


def normalize_task(value: Any, settings: dict) -> str | None:
    text = " ".join(str(value or "").split())
    aliases = {k.casefold(): v for k, v in settings["task_type_aliases"].items()}
    rules = {k.casefold(): k for k in settings["billable_rules"]}
    return aliases.get(text.casefold()) or rules.get(text.casefold())


def normalize_billable(value: Any) -> str | None:
    text = " ".join(str(value or "").strip().replace("_", " ").split())
    compact = text.casefold().replace("-", " ")
    known = {
        "billable": "Billable",
        "billable as revenue share": "Billable as Revenue Share",
        "non billable": "Non-Billable",
    }
    return known.get(compact)


def suggestions(current_billable: str, client_task: str, settings: dict) -> tuple[str, str]:
    if current_billable == "Non-Billable":
        return "", ""
    task = normalize_task(client_task, settings)
    return (task or "", settings["billable_rules"].get(task, "") if task else "")


def normalize_status(value: Any, settings: dict) -> str:
    text = " ".join(str(value or "").split())
    allowed = {s.casefold(): s for s in settings["allowed_statuses"]}
    return allowed.get(text.casefold(), settings["default_status"])
