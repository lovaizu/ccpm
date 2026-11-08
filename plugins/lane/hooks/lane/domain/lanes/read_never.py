"""Stops a role's read of the files and folders it takes."""

from __future__ import annotations

import lanes

WORDING = "Never read `<input>`."


def check(call: lanes.Call, given: dict[str, list[str]], context: lanes.Context) -> str | None:
    """The path that the call reads, where it's one of the inputs or lies under one, or None where
    the call goes on."""
    if call.tool not in ("Read", "Grep"):
        return None
    path = lanes.called_path(call) or ""
    return f"The call reads {path}." if lanes.under(path, given["input"]) else None
