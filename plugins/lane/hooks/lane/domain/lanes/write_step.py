"""Holds a step done once the role has made a file it takes, as a lane of the trace kind."""

from __future__ import annotations

import lanes

WORDING = "Make `<output>`."
TRACE = True


def traced(call: lanes.Call, given: dict[str, list[str]]) -> bool:
    """Whether the call is a Write, an Edit, or a NotebookEdit of an output."""
    return lanes.writes(call, given["output"])


def done(given: dict[str, list[str]], calls: list[lanes.Call]) -> str | None:
    """What's left to make, or None where a write of an output came back."""
    if any(traced(c, given) for c in calls):
        return None
    return f"{lanes.listed(given['output'])} isn't made yet."
