import importlib

import pytest

from web_app import HOST, PORT, page, parse_uploads, process_uploads


def multipart_body() -> tuple[str, bytes]:
    body = (
        b"--test-boundary\r\nContent-Disposition: form-data; name=\"crowdlog\"; "
        b"filename=\"crowdlog.csv\"\r\nContent-Type: text/csv\r\n\r\n"
        b"timesheet_date,member_name,minutes,memo\n\r\n"
        b"--test-boundary\r\nContent-Disposition: form-data; name=\"client\"; "
        b"filename=\"client.xlsx\"\r\nContent-Type: application/octet-stream\r\n\r\n"
        b"not-empty\r\n--test-boundary--\r\n"
    )
    return "multipart/form-data; boundary=test-boundary", body


def test_plain_page_has_two_files_and_process_button():
    content = page().decode()
    assert 'name="crowdlog"' in content
    assert 'name="client"' in content
    assert '<button type="submit">Process</button>' in content
    assert "Stop Application" not in content
    assert "<style" not in content
    assert "application workspace" in content


def test_parse_browser_uploads():
    content_type, body = multipart_body()
    uploads = parse_uploads(content_type, body)
    assert uploads["crowdlog"][0] == "crowdlog.csv"
    assert uploads["client"] == ("client.xlsx", b"not-empty")


def test_processing_requires_both_uploads():
    with pytest.raises(ValueError, match="select both"):
        process_uploads({})


def test_default_local_server_address():
    assert HOST == "127.0.0.1"
    assert PORT == 8765


def test_codespaces_defaults_to_forwarded_port(monkeypatch):
    import web_app

    monkeypatch.setenv("CODESPACES", "true")
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    reloaded = importlib.reload(web_app)
    assert reloaded.HOST == "0.0.0.0"
    assert reloaded.PORT == 8080
    monkeypatch.delenv("CODESPACES")
    importlib.reload(web_app)
