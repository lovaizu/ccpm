#!/usr/bin/env python3
"""SessionStart hook for rn, after a compact: has the conductor read the record again as /rn:up
does, since a summary drops details the record holds whole."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import record  # noqa: E402


def main():
    found = record.find(json.load(sys.stdin))
    if not found:
        return 0
    _, top, sdir = found
    rel = os.path.relpath(sdir, top)
    print(f"rn: the conversation was just summarized, and a summary drops details. Before going "
          f"on, take up the session from its record as /rn:up does: read {rel}/steering.md, every "
          f"file in {rel}/open/, and the last decision line (git log -1), and go on from its next "
          f"move.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
