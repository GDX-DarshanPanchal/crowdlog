from pathlib import Path

from .date_utils import parse_date
from .models import ClientTicket, ReviewItem
from .readers import iter_records
from .ticket_matcher import extract_one_ticket


def read_clients(path: Path) -> tuple[dict[str, ClientTicket], list[ReviewItem]]:
    clients: dict[str, ClientTicket] = {}
    invalid_tickets: set[str] = set()
    reviews: list[ReviewItem] = []
    for row_number, row, links in iter_records(path):
        ticket, error = extract_one_ticket([row.get("Ticket"), links.get("Ticket")])
        if error:
            reviews.append(ReviewItem(error, "Client", row_number, details="Ticket column is missing or invalid", original_data=str(row)))
            continue
        item = ClientTicket(ticket, str(row.get("Task") or "").strip(), str(row.get("Task Title") or "").strip(),
                            parse_date(row.get("Ticket Logged Date")), parse_date(row.get("Start Date")),
                            parse_date(row.get("End Date")), row_number)
        if ticket in invalid_tickets:
            reviews.append(ReviewItem("Duplicate/Conflicting Client Ticket", "Client", row_number, ticket=ticket,
                                      details="This ticket has multiple conflicting Client rows", original_data=str(row)))
            continue
        if ticket in clients:
            old = clients[ticket]
            if (old.task, old.title, old.logged_date, old.start_date, old.end_date) != (item.task, item.title, item.logged_date, item.start_date, item.end_date):
                reviews.append(ReviewItem("Duplicate/Conflicting Client Ticket", "Client", row_number, ticket=ticket,
                                          details=f"Also appears on client row {old.source_row}", original_data=str(row)))
                clients.pop(ticket, None)
                invalid_tickets.add(ticket)
            continue
        clients[ticket] = item
    return clients, reviews
