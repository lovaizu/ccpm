"""Checks release notes: the file given holds a version and at least one entry, each a line that
begins with `Added:` or `Fixed:`; exits 1 naming the first that does not."""

import json
import sys

with open(sys.argv[1], encoding="utf-8") as f:
    notes = json.load(f)
for entry in notes["entries"]:
    if not entry.startswith(("Added:", "Fixed:")):
        sys.exit(f"the entry {entry!r} begins with neither `Added:` nor `Fixed:`")
print(f"{len(notes['entries'])} entries of {notes['version']} checked")
