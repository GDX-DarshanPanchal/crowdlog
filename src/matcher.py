"""Match Crowdlog entries to Client data."""

from typing import Optional, Dict, List
from src.ticket_extractor import TicketExtractor
from src.utils import is_valid_jira_ticket


class Matcher:
    """Match Crowdlog records to Client data by JIRA ticket."""
    
    def __init__(self):
        """Initialize matcher."""
        self.ticket_extractor = TicketExtractor()
        self.client_lookup = {}  # ticket -> client_record
    
    def build_client_index(self, client_records: List[Dict]) -> None:
        """Build lookup index from Client records.
        
        Args:
            client_records: List of Client records
        """
        self.client_lookup = {}
        for record in client_records:
            ticket = record.get('Ticket')
            if ticket:
                # Clean up ticket value
                ticket = str(ticket).strip()
                self.client_lookup[ticket] = record
    
    def find_client_match(self, ticket: str) -> Optional[Dict]:
        """Find Client record matching a ticket.
        
        Args:
            ticket: JIRA ticket number
            
        Returns:
            Client record or None if not found
        """
        if not ticket:
            return None
        
        ticket = str(ticket).strip()
        return self.client_lookup.get(ticket)
    
    def match_crowdlog_to_client(
        self,
        crowdlog_record: Dict,
        client_records: List[Dict] = None
    ) -> tuple:
        """Match a Crowdlog record to Client data.
        
        Args:
            crowdlog_record: Crowdlog record dictionary
            client_records: List of Client records (optional, uses internal index if provided)
            
        Returns:
            Tuple of (ticket, client_record) or (None, None) if no match
        """
        # Extract ticket from Crowdlog
        ticket = self.ticket_extractor.extract_ticket(crowdlog_record)
        
        if not ticket:
            return None, None
        
        # Build index if client_records provided
        if client_records:
            self.build_client_index(client_records)
        
        # Find matching Client record
        client_match = self.find_client_match(ticket)
        
        return ticket, client_match
    
    def validate_match(self, crowdlog_record: Dict, client_record: Dict) -> bool:
        """Validate that a match is reasonable.
        
        Args:
            crowdlog_record: Crowdlog record
            client_record: Client record
            
        Returns:
            True if match is valid
        """
        if not crowdlog_record or not client_record:
            return False
        
        # Both records should have the matching ticket
        crowdlog_ticket = self.ticket_extractor.extract_ticket(crowdlog_record)
        client_ticket = client_record.get('Ticket')
        
        if not crowdlog_ticket or not client_ticket:
            return False
        
        # Tickets should match exactly
        if str(crowdlog_ticket).strip() != str(client_ticket).strip():
            return False
        
        return True
