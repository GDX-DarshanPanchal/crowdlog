# Crowdlog Monthly Report Automation - Version 1

This project automates end-of-month Crowdlog entries with descriptions for OEB.

## Version 1 Features

- Reads Crowdlog XLSX export
- Reads Client/JIRA XLSX reference file
- Extracts JIRA tickets from Crowdlog memos using regex pattern matching
- Matches Crowdlog entries to Client data by JIRA ticket
- Groups entries by Month + Employee + Ticket
- Generates monthly reporting XLSX with 18 columns
- Validates input files and produces clear error messages
- Produces "Review Needed" worksheet for records that cannot be automatically matched
- Supports both plain-text and hyperlinked JIRA tickets in Client file

## Project Structure

```
crowdlog/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration and constants
│   ├── input_reader.py        # Read XLSX input files with validation
│   ├── ticket_extractor.py    # Extract JIRA tickets from memo
│   ├── matcher.py             # Match Crowdlog to Client data
│   ├── aggregator.py          # Group and aggregate by Month/Employee/Ticket
│   ├── categorizer.py         # Normalize task types and billable status
│   ├── report_generator.py    # Generate output XLSX
│   ├── exceptions.py          # Custom exceptions
│   └── utils.py               # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_ticket_extractor.py
│   ├── test_matcher.py
│   ├── test_categorizer.py
│   ├── test_aggregator.py
│   └── test_report_generator.py
├── run.py                      # Main entry point
├── run.sh                      # Linux/Mac run script
├── run.bat                     # Windows run script
├── requirements.txt            # Python dependencies
└── README.md                   # This file

## Requirements

- Python 3.8 or higher
- openpyxl (for reading/writing XLSX files)
- Optional: pandas (for additional validation)

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Windows
```bash
run.bat <crowdlog.xlsx> <client.xlsx> <output.xlsx> [--config config.json]
```

### Linux/Mac
```bash
./run.sh <crowdlog.xlsx> <client.xlsx> <output.xlsx> [--config config.json]
```

### Python (Direct)
```bash
python run.py <crowdlog.xlsx> <client.xlsx> <output.xlsx> [--config config.json]
```

## Example

```bash
python run.py crowdlog_sample.xlsx client_sample.xlsx monthly_report_output.xlsx
```

## Output Format

The application generates an XLSX workbook with these exact 18 columns in order:

1. Resource (organization, default: "GDX")
2. Week no_ (W1, W2, W3, etc.)
3. Date (earliest Crowdlog date in group, format: DD-MMM-YY)
4. Resource (employee name from Crowdlog member_name)
5. Ticket (JIRA ticket extracted from Crowdlog memo)
6. Issue (from Client Task Title)
7. Action to Check (aggregated work dates + bullet-point memo items)
8. Resolution (JIRA ticket, e.g., OEB-1318)
9. Log (calculated hours = sum of minutes / 60)
10. Issue Log Date (from Client Ticket Logged Date)
11. Start Date (earliest start date from Client, format: DD-MMM-YY)
12. End Date/ Resolved date (from Client End Date, format: DD-MMM-YY)
13. Status (In Progress, UAT, or Live; defaults to "In Progress")
14. Final log (calculated hours = sum of minutes / 60)
15. Task type (normalized from Client Task value)
16. Billable status (from Crowdlog Billable status:name)
17. Suggested Task type (recommended based on Client Task; blank if Non-Billable)
18. Suggested Billable status (recommended based on Task Type; blank if Non-Billable)

Note: Columns 1 and 4 are both named "Resource" intentionally.

## Processing Logic

### 1. Input Validation
- Verify Crowdlog file has required columns (timesheet_date, member_name, memo, minutes, etc.)
- Verify Client file has required columns (Ticket, Task, Task Title, Start Date, End Date)
- Report clear errors if required fields are missing

### 2. JIRA Ticket Extraction
- Search Crowdlog memo field for pattern: `OEB-XXXX` (e.g., OEB-1318)
- Also check: Ticket number:name, task:Ticket number:name (only if they match JIRA pattern)
- Ignore non-JIRA values like "x" or "3H42OZ"
- If no valid ticket found → send record to "Review Needed" worksheet

### 3. Crowdlog-Client Matching
- Extract JIRA ticket from Crowdlog memo
- Look up ticket in Client file Ticket column
- If found → Link Client data (Task, Task Title, dates)
- If not found → Send record to "Review Needed" worksheet

### 4. Task Type Mapping
- Get Client Task value (e.g., "EC Operation Support")
- Normalize to standard task type:
  - "EC Operation Support" → "Operations"
  - "Operations" → "Operations"
  - "Maintenance" → "Maintenance"
  - "Additional Development" → "Additional Development"
  - Unknown values → Send to "Review Needed" worksheet
- Do NOT use Crowdlog Process:name as task type

### 5. Billable Status Handling
- Use Crowdlog "Billable status:name" as primary
- Fallback to "task:Billable status:name" if primary is empty
- **IMPORTANT: Non-Billable Exception**
  - If Crowdlog Billable status is "Non-Billable", respect that decision
  - Output: Billable status = "Non-Billable"
  - Leave Suggested Task type and Suggested Billable status BLANK
  - Do NOT suggest changing to Billable

### 6. Grouping and Aggregation
- Group records by: Reporting Month + Employee + JIRA Ticket
- Sum all minutes for the group
- Calculate hours: sum_minutes / 60
- Both Log and Final log = calculated hours
- Select earliest timesheet_date as group Date
- Combine unique work dates for Action to Check (format: MM/DD, MM/DD, ...)
- Aggregate memo items as bullet points

### 7. Action to Check Format
- First line: Unique work dates, sorted chronologically, formatted as MM/DD
  Example: `07/13, 07/15, 07/16, 07/17, 07/22, 07/27, 07/30`
- Following lines: Bullet points from Crowdlog memos
  - Remove redundant JIRA ticket prefixes
  - Remove exact duplicate descriptions
  - Do NOT invent activities

### 8. Week Number Calculation
- Calculate week within reporting month
- Monday-Sunday weeks
- First partial week containing month start = W1
- Example for July 2026:
  - 01-Jul to 05-Jul = W1
  - 06-Jul to 12-Jul = W2
  - 13-Jul to 19-Jul = W3
  - 20-Jul to 26-Jul = W4
  - 27-Jul onward = W5

### 9. Status Assignment
- Version 1: Use "In Progress" as default
- Do NOT infer from memo keywords (UAT, PROD, etc.)
- Future versions can expand status rules

### 10. Suggestions
- Suggested Task type: From Client Task value normalization
- Suggested Billable status: Based on Task Type
  - Operations → Billable
  - Maintenance → Billable as Revenue Share
  - Additional Development → Billable as Revenue Share
- **Exception: If Crowdlog is Non-Billable, leave suggestions BLANK**

## Output Worksheets

### Main Report
- All successfully processed records (18 columns)
- One row per Month + Employee + Ticket group

### Review Needed
- Records that could not be automatically processed
- Reasons: Missing JIRA ticket, Unknown task type, No Client match, etc.
- Includes: All original Crowdlog fields + reason for review

## Configuration

Optional JSON configuration file:

```json
{
  "organization_name": "GDX",
  "default_status": "In Progress",
  "task_type_mappings": {
    "EC Operation Support": "Operations",
    "Operations": "Operations",
    "Maintenance": "Maintenance",
    "Additional Development": "Additional Development"
  },
  "billable_mappings": {
    "Operations": "Billable",
    "Maintenance": "Billable as Revenue Share",
    "Additional Development": "Billable as Revenue Share"
  }
}
```

## Testing

Run unit tests:
```bash
python -m pytest tests/ -v
```

## Supported Input Files

- **Crowdlog XLSX**: Export from Crowdlog system
- **Client XLSX**: JIRA/Client reference file with ticket definitions
- Both files are read using openpyxl (supports formulas, hyperlinks, etc.)

## Error Handling

The application provides clear, actionable error messages for:
- Missing input files
- Invalid XLSX format
- Missing required columns in Crowdlog file
- Missing required columns in Client file
- Empty input files
- Invalid date formats
- Non-matching JIRA tickets

## Version History

### Version 1.0 (Current)
- Initial implementation
- Crowdlog-to-Client matching by JIRA ticket
- JIRA ticket extraction from memos using regex
- Task type normalization (4 known categories)
- Monthly grouping and aggregation
- Week number calculation (month-based)
- Review Needed worksheet for manual processing
- Non-Billable exception handling
- Configuration file support

## Future Enhancements (Version 2+)

- Complex status inference rules
- Additional task type categories
- Multi-ticket per Crowdlog entry support
- Partial month processing (weekly reports)
- Email delivery of reports
- Database integration for historical tracking
