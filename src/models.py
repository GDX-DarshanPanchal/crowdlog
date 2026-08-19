from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any


@dataclass
class ClientTicket:
    ticket: str
    task: str
    title: str
    logged_date: date | None
    start_date: date | None
    end_date: date | None
    source_row: int


@dataclass
class WorkEntry:
    source_row: int
    work_date: date
    employee: str
    ticket: str
    task_type: str
    billable_status: str
    minutes: Decimal
    memo: str
    status: str | None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReviewItem:
    reason: str
    source: str
    row: int | str
    employee: str = ""
    date: str = ""
    ticket: str = ""
    details: str = ""
    original_data: str = ""


@dataclass
class ReportRow:
    month: str
    employee: str
    ticket: str
    work_date: date
    dates: list[date]
    memos: list[str]
    minutes: Decimal
    task_type: str
    billable_status: str
    client: ClientTicket
    status: str
