"""Utility functions for Crowdlog processing."""

import re
from datetime import datetime, timedelta
from typing import Optional, List
from src.config import JIRA_TICKET_PATTERN, DATE_FORMAT


def extract_jira_ticket(text: str) -> Optional[str]:
    """Extract JIRA ticket number from text.
    
    Searches for pattern like OEB-1318.
    
    Args:
        text: Text to search for JIRA ticket
        
    Returns:
        JIRA ticket (e.g., 'OEB-1318') or None if not found
    """
    if not text:
        return None
    
    match = re.search(JIRA_TICKET_PATTERN, str(text))
    if match:
        return match.group(1)
    
    return None


def is_valid_jira_ticket(text: str) -> bool:
    """Check if text is a valid JIRA ticket.
    
    Args:
        text: Text to validate
        
    Returns:
        True if text matches JIRA ticket pattern
    """
    if not text:
        return False
    
    return bool(re.fullmatch(r'OEB-\d+', str(text).strip()))


def parse_date(date_str: str, formats: List[str] = None) -> Optional[datetime]:
    """Parse date string in multiple formats.
    
    Args:
        date_str: Date string to parse
        formats: List of format strings to try
        
    Returns:
        Datetime object or None if parsing fails
    """
    if not date_str:
        return None
    
    if formats is None:
        formats = [
            '%d-%m-%Y',      # 10-08-2026
            '%d-%b-%y',      # 19-Jun-26
            '%Y-%m-%d',      # 2026-08-10
            '%m/%d/%Y',      # 08/10/2026
            '%d/%m/%Y',      # 10/08/2026
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    return None


def format_date(dt: datetime, fmt: str = DATE_FORMAT) -> str:
    """Format datetime to string.
    
    Args:
        dt: Datetime object
        fmt: Format string
        
    Returns:
        Formatted date string
    """
    if not dt:
        return ''
    
    if isinstance(dt, str):
        dt = parse_date(dt)
    
    if not dt:
        return ''
    
    return dt.strftime(fmt)


def get_month_year(dt: datetime) -> tuple:
    """Get month and year from datetime.
    
    Args:
        dt: Datetime object
        
    Returns:
        Tuple of (month, year)
    """
    if isinstance(dt, str):
        dt = parse_date(dt)
    
    if not dt:
        return None, None
    
    return dt.month, dt.year


def calculate_week_number(dt: datetime) -> str:
    """Calculate week number within month (W1-W5).
    
    Monday-Sunday weeks.
    First partial week containing month start = W1.
    
    Example for July 2026:
    - 01-Jul to 05-Jul = W1 (partial week, Mon-Sun)
    - 06-Jul to 12-Jul = W2
    - 13-Jul to 19-Jul = W3
    - 20-Jul to 26-Jul = W4
    - 27-Jul onward = W5
    
    Args:
        dt: Datetime object
        
    Returns:
        Week number (e.g., 'W1', 'W2', etc.)
    """
    if isinstance(dt, str):
        dt = parse_date(dt)
    
    if not dt:
        return None
    
    # Get the first day of the month
    first_day = dt.replace(day=1)
    
    # Find the Monday of the week containing the first day
    # weekday(): Monday=0, Sunday=6
    days_back = first_day.weekday()
    first_week_start = first_day - timedelta(days=days_back)
    
    # Find the Monday of the week containing the target date
    target_days_back = dt.weekday()
    target_week_start = dt - timedelta(days=target_days_back)
    
    # Calculate the number of weeks from first_week_start to target_week_start
    weeks_diff = (target_week_start - first_week_start).days // 7
    week_num = weeks_diff + 1
    
    return f'W{week_num}'


def minutes_to_hours(minutes: int) -> float:
    """Convert minutes to hours.
    
    Args:
        minutes: Number of minutes
        
    Returns:
        Hours as float
    """
    if not minutes:
        return 0.0
    
    try:
        return round(float(minutes) / 60, 1)
    except (ValueError, TypeError):
        return 0.0


def clean_memo_text(memo: str) -> str:
    """Clean memo text for processing.
    
    Args:
        memo: Raw memo text
        
    Returns:
        Cleaned memo text
    """
    if not memo:
        return ''
    
    text = str(memo).strip()
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text


def extract_memo_items(memo: str) -> List[str]:
    """Extract bullet point items from memo.
    
    Args:
        memo: Memo text (may contain bullets)
        
    Returns:
        List of memo items
    """
    if not memo:
        return []
    
    text = str(memo)
    
    # Split by common bullet patterns
    items = re.split(r'[\n\-•]', text)
    
    # Clean items
    cleaned = []
    for item in items:
        item = item.strip()
        if item:
            cleaned.append(item)
    
    return cleaned


def remove_duplicate_items(items: List[str]) -> List[str]:
    """Remove duplicate items while preserving order.
    
    Args:
        items: List of items
        
    Returns:
        List with duplicates removed
    """
    seen = set()
    result = []
    
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    
    return result


def extract_work_dates(memo: str) -> List[str]:
    """Extract work dates from memo.
    
    Looks for patterns like MM/DD.
    
    Args:
        memo: Memo text
        
    Returns:
        List of dates (sorted, unique)
    """
    if not memo:
        return []
    
    # Find MM/DD or MM/DD/YY patterns
    pattern = r'\d{1,2}/\d{1,2}'
    dates = re.findall(pattern, str(memo))
    
    # Remove duplicates and sort
    unique_dates = sorted(set(dates))
    
    return unique_dates


def format_action_to_check(work_dates: List[str], memo_items: List[str]) -> str:
    """Format Action to Check field.
    
    First line: comma-separated work dates
    Following lines: memo items as bullet points
    
    Args:
        work_dates: List of work dates (MM/DD format)
        memo_items: List of memo items
        
    Returns:
        Formatted action to check text
    """
    lines = []
    
    # First line: work dates
    if work_dates:
        dates_line = ', '.join(work_dates)
        lines.append(dates_line)
    
    # Following lines: memo items
    for item in memo_items:
        if item:
            lines.append(f' - {item}')
    
    return '\n'.join(lines)
