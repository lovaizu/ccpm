"""Holds a role's end until an output it takes is there."""

from __future__ import annotations

import os

import lanes

WORDING = "End only once `<output>` is made."
END = True


def end(given: dict[str, list[str]], calls: list[lanes.Call], context: lanes.Context) -> str | None:
    """What's missing, where no output is there, or None."""
    if any(os.path.exists(p) for p in given["output"]):
        return None
    return f"{lanes.listed(given['output'])} isn't there."
