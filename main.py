from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.aggregator import aggregate
from src.client_reader import read_clients
from src.crowdlog_reader import read_work
from src.file_detector import detect_files, headers_for, CLIENT_HEADERS, CROWDLOG_HEADERS
from src.report_generator import unique_output, write_report


def load_settings(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Create monthly reports from Crowdlog and Client/JIRA files.")
    result.add_argument("--crowdlog", type=Path, help="Crowdlog .xlsx or .csv file")
    result.add_argument("--client", type=Path, help="Client/JIRA .xlsx or .csv file")
    result.add_argument("--month", help="Only generate YYYY-MM (otherwise one report per month)")
    result.add_argument("--input-dir", type=Path, default=Path("input"))
    result.add_argument("--output-dir", type=Path, default=Path("output"))
    result.add_argument("--config", type=Path, default=Path("config/settings.json"))
    return result


def run(args: argparse.Namespace) -> list[Path]:
    if bool(args.crowdlog) != bool(args.client):
        raise ValueError("Please provide both --crowdlog and --client, or put both files in the input folder.")
    crowdlog, client = (args.crowdlog, args.client) if args.crowdlog else detect_files(args.input_dir)
    for path, required, label in ((crowdlog, CROWDLOG_HEADERS, "Crowdlog"), (client, CLIENT_HEADERS, "Client/JIRA")):
        if not path.is_file():
            raise ValueError(f"The {label} file does not exist: {path}")
        missing = required - headers_for(path)
        if missing:
            raise ValueError(f"The {label} file is missing required columns: {', '.join(sorted(missing))}")
    if args.month and not __import__("re").fullmatch(r"\d{4}-(0[1-9]|1[0-2])", args.month):
        raise ValueError("--month must use YYYY-MM, for example 2026-07.")
    settings = load_settings(args.config)
    clients, client_reviews = read_clients(client)
    work, work_reviews = read_work(crowdlog, settings)
    months = sorted({entry.work_date.strftime("%Y-%m") for entry in work})
    if args.month:
        months = [args.month]
    if not months:
        raise ValueError("No valid Crowdlog work dates were found. Check the Review Needed data in the source file.")
    outputs: list[Path] = []
    for month in months:
        rows, processing_reviews = aggregate(work, clients, settings, month)
        relevant_work_reviews = [r for r in work_reviews if not r.date or _review_month(r.date) == month]
        output = unique_output(args.output_dir, month)
        write_report(output, rows, [*client_reviews, *relevant_work_reviews, *processing_reviews], settings)
        outputs.append(output)
    return outputs


def _review_month(value: str) -> str | None:
    from src.date_utils import parse_date
    parsed = parse_date(value)
    return parsed.strftime("%Y-%m") if parsed else None


def main() -> int:
    try:
        outputs = run(parser().parse_args())
        print("Success! Created:")
        for output in outputs:
            print(f"  {output}")
        print("Open each workbook and check the Review Needed worksheet.")
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"Could not create the report.\n{error}", file=sys.stderr)
        return 1
    except ImportError:
        print("Could not create the report.\nInstall the required packages with: pip install -r requirements.txt", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
