from pathlib import Path


def test_windows_launcher_is_zip_friendly():
    launcher = Path("START_CROWDLOG.bat").read_text(encoding="utf-8")
    assert 'cd /d "%~dp0"' in launcher
    assert 'set "PYTHON_CMD=py -3"' in launcher
    assert 'set "PYTHON_CMD=python"' in launcher
    assert 'set "PYTHON_CMD=python3"' in launcher
    assert "%PYTHON_CMD% -c \"import openpyxl\"" in launcher
    assert "%PYTHON_CMD% -m pip install -r requirements.txt" in launcher
    assert '%PYTHON_CMD% "%~dp0web_app.py"' in launcher
    assert "This is not an internet problem" in launcher
