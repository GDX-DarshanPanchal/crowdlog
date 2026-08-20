# Crowdlog Monthly Reporting

## HOW TO USE — NO INSTALLATION ON YOUR COMPUTER

The easiest option is **GitHub Codespaces**. It runs the application on a temporary GitHub cloud
computer. It does not use Copilot, so reaching a Copilot limit does not prevent it from running.

### Part 1 — make sure these changes are on GitHub

If you are viewing this work in Codex, click **Update branch**. That sends the committed changes to
the branch shown on GitHub. Then open the repository on GitHub and check that it contains the
`.devcontainer` folder and `web_app.py`.

If the updated branch is not the repository's main/default branch, GitHub may show **Compare & pull
request**. Open it, create the pull request, and use **Merge pull request**. If you do not have
permission to merge, the repository owner must do that step. Codespaces can also be started from
the updated branch by selecting that branch before following the steps below.

### Part 2 — start the application on GitHub

1. Open the repository's main page on GitHub.
2. Make sure the branch selector shows the branch containing these changes.
3. Press the green **Code** button.
4. Select the **Codespaces** tab. Do not select the Local tab.
5. Press **Create codespace on [branch name]**.
6. Wait while GitHub creates the Codespace. The first start can take several minutes.
7. GitHub automatically installs the required packages and starts Crowdlog.
8. A new browser tab should open with **Crowdlog Monthly Report**.

If the report tab does not open automatically:

1. In the Codespace, select the **Ports** tab in the lower panel.
2. Find port **8080**, labelled **Crowdlog Monthly Report**.
3. Select the globe/open-in-browser icon beside it.

GitHub will show an address similar to:

```text
https://something-8080.app.github.dev
```

That GitHub address—not `127.0.0.1`—is the address to bookmark while the Codespace is running.
GitHub creates it automatically. By default the forwarded port is private, so another computer
must be signed into the GitHub account that has access to the Codespace.

### Part 3 — create a report

1. Under **Crowdlog file**, press **Choose File** and select the Crowdlog export.
2. Under **Client/JIRA file**, press **Choose File** and select the reference file.
3. Press **Process**.
4. Press the download link when processing finishes.
5. Open the downloaded workbook and check the **Review Needed** worksheet.

The computer only needs a browser. Python and Excel-processing packages run inside Codespaces.

### Part 4 — stop and reopen it

To avoid using Codespaces hours when finished, return to GitHub, open your profile menu, select
**Your codespaces**, open the `...` menu beside this Codespace, and select **Stop codespace**.

Later, return to **Your codespaces** and select the Codespace name to restart it. Port 8080 and the
Crowdlog page start automatically again. A stopped Codespace keeps its files until it is deleted;
a deleted Codespace must be created again from the repository.

## If port 8080 gives HTTP ERROR 401

`401` is displayed by GitHub before the request reaches Crowdlog. It normally means the forwarded
port is private and the browser is not authenticated for the GitHub account that owns the Codespace.
It does not mean that Python or `openpyxl` failed.

Follow these steps in order:

1. Close the tab showing error 401.
2. Return to the Codespace tab and confirm that GitHub is signed into the account that created the
   Codespace.
3. Open the **Ports** tab in the lower panel.
4. Find port **8080**, right-click it, and leave **Port Visibility** set to **Private** for business
   files.
5. Use the globe/open-in-browser icon on that exact row instead of reusing an old bookmarked link.
6. If GitHub asks you to authorize access, approve it. If 401 remains, sign out of GitHub, sign in
   again with the Codespace owner's account, reopen the Codespace, and use the Ports tab again.

If port 8080 has no **Crowdlog Monthly Report** label, the Codespace was probably created before the
latest `.devcontainer` configuration was added. In the Codespace:

1. Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac).
2. Type **Rebuild Container**.
3. Select **Codespaces: Rebuild Container** or **Dev Containers: Rebuild Container**.
4. Wait for rebuilding and package installation to finish.
5. Open the **Ports** tab and use the open-in-browser icon for port 8080.

If the port still does not start, open the Codespace **Terminal**, paste the following single line,
and press Enter:

```bash
bash .devcontainer/start-web.sh
```

Wait about five seconds, return to **Ports**, and open port 8080. This is a fallback only; after a
successful container rebuild the application starts automatically.

Making the port **Public** can remove GitHub's sign-in requirement, but anyone with the address could
then open the upload page. Do not make it public for confidential Crowdlog or Client/JIRA files unless
your organization explicitly approves public port access.

## Important privacy information

Codespaces is a GitHub cloud service. The selected business files are uploaded into that Codespace
for processing. Temporary input copies are deleted after processing, while generated reports remain
in the Codespace's `output` folder until the Codespace or files are deleted. Your organization should
approve GitHub Codespaces before confidential files are processed.

## Other deployment option

`render.yaml` remains available if the repository owner wants a permanent Render website. Render
assigns the final public address after the owner connects the repository to a Render account.

## Developer commands

Local command-line use remains available but is not required for the Codespaces workflow:

```bash
python main.py --crowdlog path/to/crowdlog.xlsx --client path/to/client.xlsx
python -m pytest
```
