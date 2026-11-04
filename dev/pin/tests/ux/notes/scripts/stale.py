"""Prints the title of each note not updated since a day given as YYYY-MM-DD."""

import subprocess
import sys


def stale(since: str) -> None:
    out = subprocess.run(
        ["python3", "notes.py", "list"], capture_output=True, text=True, check=True
    )
    for line in out.stdout.splitlines():
        fields = line.split("\t")
        if fields[3][:10] < since:
            print(fields[1])


if __name__ == "__main__":
    stale(sys.argv[1])
