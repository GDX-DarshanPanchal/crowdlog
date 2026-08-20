#!/bin/sh

# Always start from the repository root, including when this script is run
# manually from a Codespaces terminal during troubleshooting.
PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$PROJECT_DIR" || exit 1

# Codespaces runs this automatically. Avoid starting a second copy when a
# sleeping Codespace resumes and the original server is still healthy.
if curl --fail --silent http://127.0.0.1:8080/health >/dev/null 2>&1; then
    exit 0
fi

HOST=0.0.0.0 PORT=8080 OPEN_BROWSER=0 nohup python web_app.py >/tmp/crowdlog-web.log 2>&1 &
