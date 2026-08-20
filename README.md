# Crowdlog Monthly Reporting

## HOW TO USE ON WINDOWS — DOWNLOAD THE ZIP

You do not need GitHub Codespaces, a pull request, a branch merge, or Copilot.

### Download

1. On GitHub, select the branch named **`crowdlog-ready-local`**.
2. Press the green **Code** button.
3. Press **Download ZIP**.
4. Open your Downloads folder.
5. Right-click the downloaded ZIP and select **Extract All**.
6. Open the extracted folder. Do not run the application from inside the ZIP preview.

### Start

1. Double-click **`START_CROWDLOG.bat`**.
2. The first run checks for the Excel package and installs it automatically if it is missing.
3. Your browser opens at **http://127.0.0.1:8765**.
4. Under **Crowdlog file**, press **Choose File** and select the Crowdlog export.
5. Under **Client/JIRA file**, press **Choose File** and select the reference file.
6. Press **Process**.
7. Press the download link when the report is ready.
8. Open the workbook and check the **Review Needed** worksheet.
9. When finished, return to the Crowdlog page and press **Stop Application**.

Keep the extracted folder. Next time, only double-click `START_CROWDLOG.bat` again. You do not need
to download the ZIP every month unless a newer version is released.

### If Windows blocks the batch file

If Windows displays a protection message, select **More info** and then **Run anyway**, but only if
you downloaded the ZIP from your trusted Crowdlog repository. Some company computers prevent all
batch files; in that case, your IT administrator must allow the file.

### If the browser says it cannot connect

Wait five seconds and refresh the page. If it still does not open, close all browser tabs for
`127.0.0.1:8765`, double-click `START_CROWDLOG.bat` again, and reopen
**http://127.0.0.1:8765**.

### If Windows says “Python was not found” or opens the Microsoft Store

This message is not caused by the internet connection. Windows has a built-in Microsoft Store
shortcut named `python`, and that shortcut can be found even when the real Python installation is
not available through the Windows PATH.

The updated launcher tries the official Python launcher (`py -3`), `python`, and `python3`, and
verifies that the command really starts Python 3.11 or newer. If none works:

1. Download Python from **https://www.python.org/downloads/windows/**.
2. Start the installer.
3. On its first screen, select **Add python.exe to PATH**.
4. Complete the installation.
5. Restart Windows.
6. Double-click `START_CROWDLOG.bat` again.

If Python is already listed under Windows **Installed apps**, choose **Modify**, then enable the
Python launcher and the option that adds Python to environment variables. The launcher now reports
package-installation errors separately instead of incorrectly calling every failure an internet
problem.

## What stays on your computer

The local address `127.0.0.1` is accessible only from the computer running the application. Input
files are processed locally. Temporary copies are deleted after processing, and generated reports
are also retained in the extracted folder's `output` directory. There is no database, Jira API,
external AI service, or API key.

## Other supported options

The project still includes optional Codespaces (`.devcontainer`) and Render (`render.yaml`)
configuration, but neither is needed for the ZIP workflow.

For developers, command-line processing remains available:

```bash
python main.py --crowdlog path/to/crowdlog.xlsx --client path/to/client.xlsx
python -m pytest
```
