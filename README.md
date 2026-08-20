# Crowdlog Monthly Reporting

## HOW TO USE

### First time only

1. Install Python 3.11 or newer.
2. Install the required packages once with `python -m pip install -r requirements.txt`.

### Every month on Windows

1. Double-click `run.bat`. You do not need to use Command Prompt.
2. Your web browser opens automatically at **http://127.0.0.1:8765**.
3. Press **Choose File** under **Crowdlog file** and select the Crowdlog export.
4. Press **Choose File** under **Client/JIRA file** and select the reference file.
5. Press **Process**.
6. Press the download link when the report is ready.
7. Open the workbook and check the **Review Needed** worksheet.

The page is intentionally plain. It runs only on your computer: `127.0.0.1` is a private local
address, not an internet website. Files are processed locally and temporary upload copies are
deleted after processing. There is no cloud connection, database, Jira API, AI service, or API key.

On macOS/Linux, run `./run.sh`; it opens the same local address. To stop the local application,
press **Stop Application** on the web page. If the browser does not open automatically, open
**http://127.0.0.1:8765**.

## Output

Each reporting month creates a workbook named `YYYY-MM_monthly_report.xlsx`. Existing reports are
never overwritten; `_2`, `_3`, and so on are added. Reports are also kept in the local `output`
folder. The workbook contains:

* **Monthly Report** — safely matched and aggregated work.
* **Review Needed** — records that require a person to check them.

Both `.xlsx` and `.csv` inputs are supported.

## Advanced command-line use

The original command-line workflow remains available but is not required for normal use:

```bash
python main.py --crowdlog path/to/crowdlog.xlsx --client path/to/client.xlsx
```

To run automated tests:

```bash
python -m pytest
```
