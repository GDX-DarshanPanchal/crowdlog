"""Extract JIRA tickets from Crowdlog data."""

from typing import Optional
from src.utils import extract_jira_ticket, is_valid_jira_ticket
from src.config import CROWDLOG_TICKET_LOOKUP_COLUMNS, CROWDLOG_MEMO_COLUMN


class TicketExtractor:
    """Extract JIRA tickets from Crowdlog records."""
    
    def __init__(self):
        """Initialize ticket extractor."""
        self.ticket_lookup_columns = CROWDLOG_TICKET_LOOKUP_COLUMNS
        self.memo_column = CROWDLOG_MEMO_COLUMN
    
    def extract_ticket(self, crowdlog_record: dict) -> Optional[str]:
        """Extract JIRA ticket from Crowdlog record.
        
        Searches in order:
        1. Ticket-related fields (only if they match JIRA pattern)
        2. Memo field
        
        Args:
            crowdlog_record: Crowdlog record as dictionary
            
        Returns:
            JIRA ticket (e.g., 'OEB-1318') or None if not found
        """
        # First, check ticket-related columns
        for column in self.ticket_lookup_columns:
            if column in crowdlog_record:
                value = crowdlog_record[column]
                if value and is_valid_jira_ticket(value):
                    return str(value).strip()
        
        # Second, search memo field
        if self.memo_column in crowdlog_record:
            memo = crowdlog_record[self.memo_column]
            ticket = extract_jira_ticket(memo)
            if ticket:
                return ticket
        
        # No ticket found
        return None
    
    def has_valid_ticket(self, crowdlog_record: dict) -> bool:
        """Check if record has a valid JIRA ticket.
        
        Args:
            crowdlog_record: Crowdlog record as dictionary
            
        Returns:
            True if valid ticket found
        """
        return self.extract_ticket(crowdlog_record) is not None
