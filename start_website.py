"""Visible one-click entry point for GitHub Codespaces.

In the Codespaces Explorer, right-click this file and select
"Run Python File in Terminal". ``web_app`` automatically uses port 8080 when
the Codespaces environment variable is present.
"""

from web_app import main


if __name__ == "__main__":
    raise SystemExit(main())
