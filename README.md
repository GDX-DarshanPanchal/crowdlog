# Crowdlog Monthly Reporting

## HOW TO USE

### Use from many computers — hosted website

This repository now includes `render.yaml`, which defines a deployable web service. After the
repository owner deploys it to a hosting account, Render provides one public address similar to:

```text
https://crowdlog-monthly-report.onrender.com
```

That exact address is assigned by Render during deployment; it cannot be created by source code or
by a temporary Codex workspace. The repository owner must connect this GitHub repository to Render
once and choose **New > Blueprint**. Render reads `render.yaml`, installs the requirements, starts
the website, and shows the final URL. No files need to be installed on the computers that use it.

At the hosted address:

1. Press **Choose File** under **Crowdlog file**.
2. Press **Choose File** under **Client/JIRA file**.
3. Press **Process**.
4. Download the generated report.
5. Check the **Review Needed** worksheet.

Important: on a hosted service, selected business files are uploaded to that hosting service for
processing. Temporary input copies are deleted after processing, but your organization should
approve the selected host before confidential files are used.

### Optional use on one computer

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

The page is intentionally plain. In local mode, `127.0.0.1` is a private address and files stay on
that computer. In hosted mode, the same application is reached through the hosting provider's URL.
Temporary upload copies are deleted after processing. There is no database, Jira API, AI service,
or API key.

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
