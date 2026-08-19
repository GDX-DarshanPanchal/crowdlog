# Crowdlog Monthly Reporting

## HOW TO USE

1. Put your Crowdlog export in the `input` folder.
2. Put your Client/JIRA file in the `input` folder.
3. Double-click `run.bat` on Windows, or run `python main.py`.
4. Open the `output` folder.
5. Open the generated monthly report.
6. Check the **Review Needed** sheet for anything requiring attention.

### One-time installation

Install Python 3.11 or newer, then open a command prompt in this folder and run:

```bash
pip install -r requirements.txt
```

The program is completely local. It has no UI, database, cloud, Jira API, AI service, or API key.

## Running the report

The simplest command automatically identifies both input files by their columns:

```bash
python main.py
```

To provide files in another location:

```bash
python main.py --crowdlog path/to/crowdlog.xlsx --client path/to/client.xlsx
```

To create only one month when an export contains several months:

```bash
python main.py --month 2026-07
```

Both `.xlsx` and `.csv` inputs are supported. Each month produces a new file named
`YYYY-MM_monthly_report.xlsx`. Existing output is never overwritten; a suffix such as `_2`
is added instead.

## What the workbook contains

* **Monthly Report** contains safely matched and aggregated Employee + Jira Ticket + Month work.
* **Review Needed** explains missing tickets, unknown categories, conflicts, invalid values, and
  other records that need a person to check them. A problem in one row does not stop valid work.

Minutes are summed before conversion to hours. Logged task and billing values are retained;
suggestions come from the Client/JIRA task. Intentional Non-Billable work never receives a
billable suggestion.

Business rules, the `GDX` organization value, and employee aliases are in
`config/settings.json` so they can be maintained without changing Python code.

## Troubleshooting

* Keep exactly one Crowdlog file and one Client/JIRA file in `input` for automatic detection.
* Close input/output workbooks in Excel before running the program.
* Read the plain-language console message if file columns cannot be identified.
* Always inspect **Review Needed** before using a report.

## Tests

```bash
python -m pytest
```
