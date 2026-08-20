"""Small local desktop window for running the Crowdlog report.

The processing remains in ``main.py`` so the command-line and desktop workflows
always apply the same business rules.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

from main import run


SUPPORTED_EXTENSIONS = {".xlsx", ".csv"}


def validate_selected_files(crowdlog: str, client: str) -> tuple[Path, Path]:
    """Validate UI selections and return safe paths for the processing layer."""
    if not crowdlog or not client:
        raise ValueError("Please select both the Crowdlog file and the Client/JIRA file.")
    crowdlog_path = Path(crowdlog)
    client_path = Path(client)
    for path, label in ((crowdlog_path, "Crowdlog"), (client_path, "Client/JIRA")):
        if not path.is_file():
            raise ValueError(f"The selected {label} file could not be found:\n{path}")
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"The {label} file must be an Excel (.xlsx) or CSV (.csv) file.")
    if crowdlog_path.resolve() == client_path.resolve():
        raise ValueError("Please select two different files.")
    return crowdlog_path, client_path


def process_selected_files(crowdlog: str, client: str, project_dir: Path) -> list[Path]:
    """Run the existing report pipeline for files selected in the window."""
    crowdlog_path, client_path = validate_selected_files(crowdlog, client)
    arguments = SimpleNamespace(
        crowdlog=crowdlog_path,
        client=client_path,
        month=None,
        input_dir=project_dir / "input",
        output_dir=project_dir / "output",
        config=project_dir / "config" / "settings.json",
    )
    return run(arguments)


def open_folder(path: Path) -> None:
    """Open a folder using the operating system's normal file browser."""
    if sys.platform == "win32":
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


def main() -> int:
    # Tkinter ships with normal Python installations and adds no web/cloud dependency.
    import tkinter as tk
    from tkinter import filedialog, messagebox

    project_dir = Path(__file__).resolve().parent
    output_dir = project_dir / "output"
    root = tk.Tk()
    root.title("Crowdlog Monthly Report")
    root.resizable(False, False)

    crowdlog_value = tk.StringVar()
    client_value = tk.StringVar()
    status_value = tk.StringVar(value="Select both files, then press Process.")

    frame = tk.Frame(root, padx=16, pady=16)
    frame.grid(row=0, column=0)

    def select_file(target: tk.StringVar, title: str) -> None:
        selected = filedialog.askopenfilename(
            title=title,
            filetypes=(("Excel or CSV files", "*.xlsx *.csv"), ("Excel files", "*.xlsx"),
                       ("CSV files", "*.csv"), ("All files", "*.*")),
        )
        if selected:
            target.set(selected)
            status_value.set("Select both files, then press Process.")

    tk.Label(frame, text="Crowdlog file").grid(row=0, column=0, sticky="w", pady=(0, 4))
    tk.Entry(frame, textvariable=crowdlog_value, width=62, state="readonly").grid(row=1, column=0, padx=(0, 8))
    tk.Button(frame, text="Select Crowdlog File", command=lambda: select_file(crowdlog_value, "Select Crowdlog file")).grid(row=1, column=1)

    tk.Label(frame, text="Client/JIRA file").grid(row=2, column=0, sticky="w", pady=(14, 4))
    tk.Entry(frame, textvariable=client_value, width=62, state="readonly").grid(row=3, column=0, padx=(0, 8))
    tk.Button(frame, text="Select Client/JIRA File", command=lambda: select_file(client_value, "Select Client/JIRA file")).grid(row=3, column=1)

    def process() -> None:
        process_button.configure(state="disabled")
        status_value.set("Processing... Please wait.")
        root.update_idletasks()
        try:
            outputs = process_selected_files(crowdlog_value.get(), client_value.get(), project_dir)
        except Exception as error:  # UI boundary: show processing failures without a traceback.
            status_value.set("The report could not be created.")
            messagebox.showerror("Could not create report", str(error))
        else:
            names = "\n".join(path.name for path in outputs)
            status_value.set(f"Finished. Created: {', '.join(path.name for path in outputs)}")
            messagebox.showinfo("Report created", f"Your report is ready in the output folder:\n\n{names}")
            open_output_button.configure(state="normal")
        finally:
            process_button.configure(state="normal")

    process_button = tk.Button(frame, text="Process", width=18, command=process)
    process_button.grid(row=4, column=0, sticky="w", pady=(18, 0))
    open_output_button = tk.Button(frame, text="Open Output Folder", width=20,
                                   command=lambda: open_folder(output_dir), state="disabled")
    open_output_button.grid(row=4, column=1, pady=(18, 0))
    tk.Label(frame, textvariable=status_value, anchor="w", justify="left", wraplength=620).grid(
        row=5, column=0, columnspan=2, sticky="w", pady=(16, 0))

    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
