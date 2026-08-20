from pathlib import Path

import pytest

from ui import validate_selected_files


def test_ui_requires_both_files(tmp_path: Path):
    crowdlog = tmp_path / "crowdlog.xlsx"
    crowdlog.touch()
    with pytest.raises(ValueError, match="select both"):
        validate_selected_files(str(crowdlog), "")


def test_ui_accepts_xlsx_and_csv(tmp_path: Path):
    crowdlog = tmp_path / "crowdlog.xlsx"
    client = tmp_path / "client.csv"
    crowdlog.touch()
    client.touch()
    assert validate_selected_files(str(crowdlog), str(client)) == (crowdlog, client)


def test_ui_rejects_same_or_unsupported_file(tmp_path: Path):
    text_file = tmp_path / "file.txt"
    text_file.touch()
    with pytest.raises(ValueError, match="Excel"):
        validate_selected_files(str(text_file), str(tmp_path / "missing.csv"))
    spreadsheet = tmp_path / "file.xlsx"
    spreadsheet.touch()
    with pytest.raises(ValueError, match="different"):
        validate_selected_files(str(spreadsheet), str(spreadsheet))
