"""Prints how many notes each tag has."""

import subprocess
from collections import Counter


def report() -> None:
    out = subprocess.run(
        ["python3", "notes.py", "list"], capture_output=True, text=True, check=True
    )
    counts: Counter[str] = Counter()
    for line in out.stdout.splitlines():
        counts.update(line.split("\t")[2].split(","))
    for tag, count in counts.most_common():
        print(f"{tag}: {count}")
