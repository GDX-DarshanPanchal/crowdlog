from decimal import Decimal, InvalidOperation
from pathlib import Path

from .categorizer import normalize_billable, normalize_status, normalize_task
from .date_utils import parse_date
from .models import ReviewItem, WorkEntry
from .readers import iter_records
from .ticket_matcher import extract_one_ticket


TICKET_FIELDS = ("Ticket number:management_code", "Ticket number:name", "task:Ticket number:management_code", "task:Ticket number:name", "memo")
TASK_FIELDS = ("task_group_name", "task_name", "Ticket number:name", "task:Ticket number:name")


def read_work(path: Path, settings: dict) -> tuple[list[WorkEntry], list[ReviewItem]]:
    work: list[WorkEntry] = []
    reviews: list[ReviewItem] = []
    for number, row, _links in iter_records(path):
        employee = str(row.get("member_name") or "").strip()
        date = parse_date(row.get("timesheet_date"))
        ticket, ticket_error = extract_one_ticket(row.get(field) for field in TICKET_FIELDS)
        try:
            minutes = Decimal(str(row.get("minutes"))).quantize(Decimal("0.0001"))
            if minutes < 0:
                raise InvalidOperation
        except (InvalidOperation, TypeError, ValueError):
            minutes = Decimal(0)
            ticket_error = ticket_error or "Invalid Minutes"
        task = next((normalize_task(row.get(field), settings) for field in TASK_FIELDS if normalize_task(row.get(field), settings)), None)
        billable_raw = row.get("Billable status:name") or row.get("task:Billable status:name")
        billable = normalize_billable(billable_raw)
        reason = ticket_error
        if not date:
            reason = reason or "Invalid Date"
        if not employee:
            reason = reason or "Missing Employee"
        if not task:
            reason = reason or "Unknown Crowdlog Task Type"
        if not billable:
            reason = reason or "Unknown Billable Status"
        if reason:
            reviews.append(ReviewItem(reason, "Crowdlog", number, employee, str(row.get("timesheet_date") or ""), ticket or "",
                                      "Record was not safe to process", str(row)))
            # A sample export can lack a business task field. Matching Client task is handled later,
            # but all other structural errors prevent safe processing.
            if reason != "Unknown Crowdlog Task Type":
                continue
        if date and employee and ticket and billable:
            work.append(WorkEntry(number, date, employee, ticket, task or "", billable, minutes,
                                  str(row.get("memo") or ""), normalize_status(row.get("progress"), settings), row))
    return work, reviews
