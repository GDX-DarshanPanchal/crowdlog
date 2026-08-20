from collections import defaultdict
from decimal import Decimal

from .categorizer import normalize_task
from .date_utils import month_key
from .models import ClientTicket, ReportRow, ReviewItem, WorkEntry


def hours(minutes: Decimal | int) -> Decimal:
    return Decimal(minutes) / Decimal(60)


def aggregate(entries: list[WorkEntry], clients: dict[str, ClientTicket], settings: dict,
              selected_month: str | None = None) -> tuple[list[ReportRow], list[ReviewItem]]:
    reviews: list[ReviewItem] = []
    valid: list[WorkEntry] = []
    for entry in entries:
        if selected_month and month_key(entry.work_date) != selected_month:
            continue
        client = clients.get(entry.ticket)
        if not client:
            reviews.append(ReviewItem("Client Ticket Not Found", "Crowdlog", entry.source_row, entry.employee,
                                      str(entry.work_date), entry.ticket, "No exact Client/JIRA match", str(entry.raw)))
            continue
        client_task = normalize_task(client.task, settings)
        if not client_task:
            reviews.append(ReviewItem("Unknown Client Task Type", "Client", client.source_row, ticket=entry.ticket,
                                      details=client.task))
            continue
        # Actual sample has no Crowdlog business category. Use the matched client category as
        # a conservative fallback and retain the existing review warning from the reader.
        entry.task_type = entry.task_type or client_task
        valid.append(entry)

    base: dict[tuple[str, str, str], list[WorkEntry]] = defaultdict(list)
    for entry in valid:
        base[(month_key(entry.work_date), entry.employee, entry.ticket)].append(entry)
    rows: list[ReportRow] = []
    for (month, employee, ticket), group in base.items():
        tasks = {e.task_type for e in group}
        statuses = {e.billable_status for e in group}
        if len(tasks) > 1:
            reviews.append(ReviewItem("Conflicting Crowdlog Task Types", "Crowdlog", ", ".join(str(e.source_row) for e in group), employee, ticket=ticket, details=", ".join(sorted(tasks))))
        if len(statuses) > 1:
            reviews.append(ReviewItem("Conflicting Billable Statuses", "Crowdlog", ", ".join(str(e.source_row) for e in group), employee, ticket=ticket, details=", ".join(sorted(statuses))))
        # Split conflicts so every minute remains visible and no value is silently selected.
        splits: dict[tuple[str, str], list[WorkEntry]] = defaultdict(list)
        for entry in group:
            splits[(entry.task_type, entry.billable_status)].append(entry)
        for (task, billable), subgroup in splits.items():
            dates = sorted({e.work_date for e in subgroup})
            rows.append(ReportRow(month, employee, ticket, dates[0], dates, [e.memo for e in subgroup],
                                  sum((e.minutes for e in subgroup), Decimal(0)), task, billable,
                                  clients[ticket], subgroup[0].status or settings["default_status"]))
    return sorted(rows, key=lambda r: (r.month, r.work_date, r.employee, r.ticket, r.task_type, r.billable_status)), reviews
