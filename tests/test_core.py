from datetime import date
from decimal import Decimal

import pytest

from src.action_summary import action_summary
from src.aggregator import aggregate, hours
from src.categorizer import normalize_billable, normalize_task, suggestions
from src.date_utils import parse_date, week_in_month
from src.models import ClientTicket, WorkEntry
from src.ticket_matcher import extract_tickets


@pytest.fixture
def settings():
    return {
        "resource_group": "GDX", "resource_aliases": {"Panchal Darshan": "Darshan"},
        "task_type_aliases": {"EC Operation Support": "Operations"},
        "billable_rules": {"Operations": "Billable", "Maintenance": "Billable as Revenue Share",
                           "Additional Development": "Billable as Revenue Share"},
        "allowed_statuses": ["In Progress", "UAT", "Live"], "default_status": "In Progress",
    }


@pytest.mark.parametrize(("value", "expected"), [
    ("OEB-1318 AW26 Build review", ["OEB-1318"]),
    ("https://jira.example/browse/oeb-1318", ["OEB-1318"]),
    ("x", []), ("3H42OZ", []), ("EC Operation Support", []),
])
def test_ticket_extraction(value, expected):
    assert extract_tickets(value) == expected


def test_rules(settings):
    assert hours(Decimal(1110)) == Decimal("18.5")
    assert normalize_task("EC Operation Support", settings) == "Operations"
    assert settings["billable_rules"] == {"Operations": "Billable", "Maintenance": "Billable as Revenue Share",
                                           "Additional Development": "Billable as Revenue Share"}
    assert normalize_billable("NON BILLABLE") == "Non-Billable"
    assert suggestions("Non-Billable", "EC Operation Support", settings) == ("", "")


def test_dates_and_week():
    assert parse_date("10-08-2026") == date(2026, 8, 10)
    assert parse_date("19-Jun-26") == date(2026, 6, 19)
    assert week_in_month(date(2026, 7, 13)) == "W3"


def test_action_summary():
    assert action_summary([date(2026, 7, 15), date(2026, 7, 13)],
                          ["OEB-1318  AW26 Build review", "OEB-1318 AW26 Build review"], "OEB-1318") == (
                              "07/13, 07/15\n- AW26 Build review")


def test_aggregation_keeps_groups_separate(settings):
    client = ClientTicket("OEB-1", "EC Operation Support", "Issue", None, None, None, 2)
    entries = [
        WorkEntry(2, date(2026, 7, 1), "A", "OEB-1", "Operations", "Billable", Decimal(30), "one", None),
        WorkEntry(3, date(2026, 7, 2), "A", "OEB-1", "Operations", "Billable", Decimal(60), "two", None),
        WorkEntry(4, date(2026, 7, 2), "B", "OEB-1", "Operations", "Billable", Decimal(15), "", None),
        WorkEntry(5, date(2026, 8, 2), "A", "OEB-1", "Operations", "Billable", Decimal(20), "", None),
    ]
    rows, reviews = aggregate(entries, {"OEB-1": client}, settings)
    assert not reviews
    assert [(r.month, r.employee, r.ticket, r.minutes) for r in rows] == [
        ("2026-07", "A", "OEB-1", Decimal(90)), ("2026-07", "B", "OEB-1", Decimal(15)),
        ("2026-08", "A", "OEB-1", Decimal(20)),
    ]
