"""Local browser interface for Crowdlog reporting.

The server listens only on this computer (127.0.0.1). Uploaded files are placed
in a temporary directory, processed locally, and deleted immediately afterward.
"""

from __future__ import annotations

import html
import os
import secrets
import shutil
import tempfile
import threading
import webbrowser
from email.parser import BytesParser
from email.policy import default
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import quote, unquote, urlparse

from main import run

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8765"))
MAX_UPLOAD_BYTES = 100 * 1024 * 1024
PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "output"
DOWNLOADS: dict[str, Path] = {}
DOWNLOADS_LOCK = threading.Lock()


def page(message: str = "", downloads: list[Path] | None = None) -> bytes:
    """Create the deliberately plain application page."""
    result = ""
    if message:
        result += f"<p><strong>{html.escape(message)}</strong></p>"
    if downloads:
        result += "<p>Your report is ready:</p><ul>"
        for path in downloads:
            token = secrets.token_urlsafe(24)
            with DOWNLOADS_LOCK:
                DOWNLOADS[token] = path
            result += f'<li><a href="/download/{token}/{quote(path.name)}">Download {html.escape(path.name)}</a></li>'
        result += "</ul><p>Open the workbook and check the Review Needed worksheet.</p>"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Crowdlog Monthly Report</title></head>
<body>
<h1>Crowdlog Monthly Report</h1>
<p>Select both files and press Process. Your files stay on this computer.</p>
{result}
<form method="post" action="/process" enctype="multipart/form-data">
  <p><label>Crowdlog file<br><input type="file" name="crowdlog" accept=".xlsx,.csv" required></label></p>
  <p><label>Client/JIRA file<br><input type="file" name="client" accept=".xlsx,.csv" required></label></p>
  <p><button type="submit">Process</button></p>
</form>
<form method="post" action="/shutdown"><p><button type="submit">Stop Application</button></p></form>
</body></html>""".encode("utf-8")


def parse_uploads(content_type: str, body: bytes) -> dict[str, tuple[str, bytes]]:
    """Parse the two browser uploads using only the Python standard library."""
    message = BytesParser(policy=default).parsebytes(
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode() + body
    )
    uploads: dict[str, tuple[str, bytes]] = {}
    if not message.is_multipart():
        return uploads
    for part in message.iter_parts():
        name = part.get_param("name", header="content-disposition")
        filename = part.get_filename()
        if name and filename:
            uploads[name] = (Path(filename).name, part.get_payload(decode=True) or b"")
    return uploads


def process_uploads(uploads: dict[str, tuple[str, bytes]]) -> list[Path]:
    """Validate, temporarily save, and process browser uploads."""
    if "crowdlog" not in uploads or "client" not in uploads:
        raise ValueError("Please select both the Crowdlog file and the Client/JIRA file.")
    temporary = Path(tempfile.mkdtemp(prefix="crowdlog_"))
    try:
        paths: dict[str, Path] = {}
        for field in ("crowdlog", "client"):
            filename, contents = uploads[field]
            suffix = Path(filename).suffix.lower()
            if suffix not in {".xlsx", ".csv"}:
                raise ValueError("Files must be Excel (.xlsx) or CSV (.csv) files.")
            if not contents:
                raise ValueError(f"The selected {field} file is empty.")
            path = temporary / f"{field}{suffix}"
            path.write_bytes(contents)
            paths[field] = path
        arguments = SimpleNamespace(
            crowdlog=paths["crowdlog"], client=paths["client"], month=None,
            input_dir=PROJECT_DIR / "input", output_dir=OUTPUT_DIR,
            config=PROJECT_DIR / "config" / "settings.json",
        )
        return run(arguments)
    finally:
        shutil.rmtree(temporary, ignore_errors=True)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        requested = urlparse(self.path).path
        if requested == "/health":
            self._send(200, b"ok", "text/plain; charset=utf-8")
            return
        if requested == "/":
            self._send(200, page(), "text/html; charset=utf-8")
            return
        if requested.startswith("/download/"):
            parts = requested.removeprefix("/download/").split("/", 1)
            token = parts[0]
            filename = Path(unquote(parts[1])).name if len(parts) == 2 else ""
            with DOWNLOADS_LOCK:
                path = DOWNLOADS.get(token)
            if path and path.is_file() and path.name == filename and path.suffix.lower() == ".xlsx":
                self._send(200, path.read_bytes(),
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           f'attachment; filename="{filename}"')
                return
        self._send(404, page("That page or report was not found."), "text/html; charset=utf-8")

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        requested = urlparse(self.path).path
        if requested == "/shutdown":
            content = b"<!doctype html><html><body><p>Crowdlog has stopped. You may close this page.</p></body></html>"
            self._send(200, content, "text/html; charset=utf-8")
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return
        if requested != "/process":
            self._send(404, page("That page was not found."), "text/html; charset=utf-8")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_UPLOAD_BYTES:
                raise ValueError("The upload is empty or larger than 100 MB.")
            uploads = parse_uploads(self.headers.get("Content-Type", ""), self.rfile.read(length))
            outputs = process_uploads(uploads)
        except Exception as error:  # HTTP boundary: return a readable page rather than a traceback.
            self._send(400, page(f"Could not create the report: {error}"), "text/html; charset=utf-8")
            return
        self._send(200, page("Processing finished successfully.", outputs), "text/html; charset=utf-8")

    def _send(self, status: int, content: bytes, content_type: str,
              disposition: str | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        if disposition:
            self.send_header("Content-Disposition", disposition)
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> int:
    OUTPUT_DIR.mkdir(exist_ok=True)
    browser_host = "127.0.0.1" if HOST == "0.0.0.0" else HOST
    address = f"http://{browser_host}:{PORT}"
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Crowdlog is ready at {address}")
    print("Keep this window open while using the page. Close it to stop the application.")
    if os.environ.get("OPEN_BROWSER", "1") == "1":
        threading.Timer(0.5, lambda: webbrowser.open(address)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
