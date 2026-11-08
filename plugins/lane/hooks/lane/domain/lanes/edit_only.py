"""Lets a role change its output, once it's made, only with Edit, which Claude Code lets go only
after a Read of the file, so the role has read what it changes."""

from __future__ import annotations

import os

import lanes

WORDING = "Once `<output>` is made, change it only with Edit."


def check(call: lanes.Call, given: dict[str, list[str]], context: lanes.Context) -> str | None:
    """What the role must do instead, where the call writes an output that's there whole, or
    changes it with NotebookEdit, or None where the call goes on."""
    if call.tool not in ("Write", "NotebookEdit"):
        return None
    path = lanes.called_path(call) or ""
    if not lanes.under(path, given["output"]):
        return None
    if call.tool == "NotebookEdit":
        return f"`{path}` changes only with Edit."
    return f"`{path}` is there, so change it with Edit." if os.path.exists(path) else None
