"""Holds a step done once the role has read a file it takes to its end, as a lane of the trace
kind."""

from __future__ import annotations

import lanes

WORDING = "Read `<input>` to its end."
TRACE = True
# The lines that a Read with no limit reads, as the Read tool documents it.
READ_LINES = 2000


def traced(call: lanes.Call, given: dict[str, list[str]]) -> bool:
    """Whether the call is a Read of an input."""
    return call.tool == "Read" and lanes.under(lanes.called_path(call) or "", given["input"])


def done(given: dict[str, list[str]], calls: list[lanes.Call]) -> str | None:
    """What's left to read, or None where the Reads kept cover every line of an input."""
    missing = []
    for path in given["input"]:
        left = _unread(path, [c for c in calls if traced(c, {"input": [path]})])
        if left is None:
            return None
        missing.append(left)
    return missing[0]


def _unread(path: str, reads: list[lanes.Call]) -> str | None:
    """What of the file the Reads leave unread, or None where they cover every line. A Read that
    the guard kept gives the file's lines as they stood then, under `lines`."""
    counts = [r.input["lines"] for r in reads if isinstance(r.input.get("lines"), int)]
    if counts:
        count = counts[-1]
    else:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                count = len(f.read().splitlines())
        except OSError:
            return f"`{path}` isn't there to read."
    if not reads:
        return f"`{path}` is unread."
    covered = set()
    for read in reads:
        first = max(1, int(read.input.get("offset") or 1))
        covered.update(range(first, first + int(read.input.get("limit") or READ_LINES)))
    gaps = [n for n in range(1, count + 1) if n not in covered]
    if not gaps:
        return None
    end = gaps[0]
    while end + 1 in gaps:
        end += 1
    return f"`{path}` has lines {gaps[0]} to {end} unread."
