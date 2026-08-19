#!/usr/bin/env python3
"""
Validate CSV structure and alignment.
Do NOT make assumptions about data; report exactly what is present.
"""

import csv
import re

def validate_csv(file_path):
    """Validate CSV structure and report exact field counts and alignment."""
    print(f"\n{'='*120}")
    print(f"VALIDATING: {file_path}")
    print(f"{'='*120}\n")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        if not rows:
            print("ERROR: File is empty")
            return
        
        # Header row
        header_row = rows[0]
        num_headers = len(header_row)
        print(f"HEADER COUNT: {num_headers}")
        print(f"HEADERS:")
        for idx, header in enumerate(header_row, 1):
            print(f"  {idx:2d}. {repr(header)}")
        
        # Sample rows
        print(f"\n\nDATA ROWS VALIDATION:")
        for row_num, row in enumerate(rows[1:], 2):
            num_fields = len(row)
            alignment_status = "✓ ALIGNED" if num_fields == num_headers else f"✗ MISALIGNED ({num_fields} fields vs {num_headers} headers)"
            print(f"\nRow {row_num}: {num_fields} fields - {alignment_status}")
            
            if num_fields != num_headers:
                print(f"  DIFFERENCE: {num_fields - num_headers} fields")
            
            # Show first few fields and last few fields
            print(f"  First 5 fields:")
            for idx, field in enumerate(row[:5], 1):
                print(f"    {idx}. {repr(field)[:80]}")
            
            if num_fields > 10:
                print(f"  ... ({num_fields - 10} more fields)")
                print(f"  Last 5 fields:")
                for idx, field in enumerate(row[-5:], num_fields - 4):
                    print(f"    {idx}. {repr(field)[:80]}")
            else:
                print(f"  Remaining fields:")
                for idx, field in enumerate(row[5:], 6):
                    print(f"    {idx}. {repr(field)[:80]}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

def extract_jira_ticket(text):
    """Extract JIRA ticket pattern (e.g., OEB-1318) from text."""
    if not text:
        return None
    pattern = r'\b(OEB-\d+)\b'
    match = re.search(pattern, text)
    return match.group(1) if match else None

def analyze_crowdlog_tickets(file_path):
    """Analyze Crowdlog for JIRA ticket presence and location."""
    print(f"\n\n{'='*120}")
    print(f"CROWDLOG TICKET ANALYSIS: {file_path}")
    print(f"{'='*120}\n")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, 2):
                print(f"Row {row_num}:")
                
                # Check each field for JIRA ticket pattern
                fields_with_tickets = []
                for field_name, field_value in row.items():
                    if field_value:
                        ticket = extract_jira_ticket(field_value)
                        if ticket:
                            fields_with_tickets.append((field_name, field_value, ticket))
                
                if fields_with_tickets:
                    print(f"  JIRA tickets found:")
                    for field_name, field_value, ticket in fields_with_tickets:
                        print(f"    Field '{field_name}': {repr(field_value)[:80]} → Extracted: {ticket}")
                else:
                    print(f"  No JIRA tickets found")
                
                # Show specific fields
                print(f"\n  Specific fields:")
                for key in ['Ticket number:name', 'memo', 'Process:name', 'Billable status:name']:
                    value = row.get(key)
                    print(f"    {key}: {repr(value)}")
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

def validate_monthly_report(file_path):
    """Validate monthly report columns and sample values."""
    print(f"\n\n{'='*120}")
    print(f"MONTHLY REPORT VALIDATION: {file_path}")
    print(f"{'='*120}\n")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        if len(rows) < 2:
            print("ERROR: Insufficient rows")
            return
        
        header_row = rows[0]
        print(f"COLUMNS ({len(header_row)} total):")
        for idx, header in enumerate(header_row, 1):
            print(f"  {idx:2d}. {repr(header)}")
        
        # Check for duplicate column names
        from collections import Counter
        header_counts = Counter(header_row)
        duplicates = {h: count for h, count in header_counts.items() if count > 1}
        if duplicates:
            print(f"\n⚠️  DUPLICATE COLUMN NAMES:")
            for header, count in duplicates.items():
                positions = [i+1 for i, h in enumerate(header_row) if h == header]
                print(f"    '{header}' appears {count} times at positions: {positions}")
        
        # Analyze data row(s)
        print(f"\n\nDATA ROWS:")
        for row_num, row in enumerate(rows[1:], 2):
            print(f"\nRow {row_num}: ({len(row)} fields)")
            
            # Map columns to values
            for col_idx, (header, value) in enumerate(zip(header_row, row), 1):
                if value:
                    value_display = repr(value)[:100]
                    print(f"  Col {col_idx:2d} [{header:25s}]: {value_display}")
                else:
                    print(f"  Col {col_idx:2d} [{header:25s}]: [EMPTY]")
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Validate each file
    validate_csv("crowdlog_sample.csv")
    validate_csv("client_sample.csv")
    validate_csv("monthly_report_example.csv")
    
    # Analyze Crowdlog tickets
    analyze_crowdlog_tickets("crowdlog_sample.csv")
    
    # Validate monthly report details
    validate_monthly_report("monthly_report_example.csv")
    
    print("\n\n" + "="*120)
    print("VALIDATION COMPLETE")
    print("="*120)
