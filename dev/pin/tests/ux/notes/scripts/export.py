"""Writes the notes' titles and tags to notes.csv."""

import subprocess


def export() -> None:
    out = subprocess.run(
        ["python3", "notes.py", "list"], capture_output=True, text=True, check=True
    )
    with open("notes.csv", "w") as f:
        for line in out.stdout.splitlines():
            _, title, tags, _ = line.split("\t")
            f.write(f"{title},{tags}\n")
