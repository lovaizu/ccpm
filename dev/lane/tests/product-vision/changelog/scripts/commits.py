"""Prints the commits of the part given, `first` or `second`, a line each."""

import sys

PARTS = {
    "first": ["Add a search over the notes", "Fix a crash on an empty note"],
    "second": ["Add tags to notes"],
}
part = sys.argv[1] if len(sys.argv) > 1 else ""
if part not in PARTS:
    sys.exit(f"no part {part!r}; give `first` or `second`")
print("\n".join(PARTS[part]))
