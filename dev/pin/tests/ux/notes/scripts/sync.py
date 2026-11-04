"""Sends each note changed since the last sync to the calendar."""

import subprocess
from datetime import datetime, timezone

LAST = datetime(2026, 11, 1, tzinfo=timezone.utc)


def changed() -> list[str]:
    out = subprocess.run(
        ["python3", "notes.py", "list"], capture_output=True, text=True, check=True
    )
    found = []
    for line in out.stdout.splitlines():
        fields = line.split("\t")
        if datetime.fromisoformat(fields[3]) > LAST:
            found.append(fields[1])
    return found
