from pathlib import Path


def test_windows_launcher_is_zip_friendly():
    launcher = Path("START_CROWDLOG.bat").read_text(encoding="utf-8")
    assert 'cd /d "%~dp0"' in launcher
    assert 'python -c "import openpyxl"' in launcher
    assert "python -m pip install -r requirements.txt" in launcher
    assert 'pythonw "%~dp0web_app.py"' in launcher
    assert "http://127.0.0.1:8765" in launcher
