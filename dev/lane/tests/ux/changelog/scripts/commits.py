"""Prints the commits of the part given, `first` or `second`, a line each. The second part comes
45 seconds late, as from a slow mirror, so that a run reading it ends well after a run reading the
first: the trial of runs at once has the orchestrator's start between their ends tried."""

import sys
import time

PARTS = {
    "first": ["Add a search over the notes", "Fix a crash on an empty note"],
    "second": ["Add tags to notes"],
}
part = sys.argv[1] if len(sys.argv) > 1 else ""
if part not in PARTS:
    sys.exit(f"no part {part!r}; give `first` or `second`")
if part == "second":
    time.sleep(45)
print("\n".join(PARTS[part]))
