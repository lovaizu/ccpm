"""Holds a role's writes to the files and folders it takes."""

from __future__ import annotations

import lanes

WORDING = "Write only `<output>`."


def check(call: lanes.Call, given: dict[str, list[str]], context: lanes.Context) -> str | None:
    """The path that the call writes, where it lies outside the outputs, or None where the call
    goes on."""
    if call.tool not in ("Write", "Edit", "NotebookEdit"):
        return None
    path = lanes.called_path(call)
    if path is not None and lanes.under(path, given["output"]):
        return None
    return f"The call writes {path}."
