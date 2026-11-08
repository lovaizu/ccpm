"""Holds a role's reads to the files and folders it takes, beside the forms of its in_form lanes
and its own part."""

from __future__ import annotations

import lanes

WORDING = "Read only `<input>`."


def check(call: lanes.Call, given: dict[str, list[str]], context: lanes.Context) -> str | None:
    """The path that the call reads, where it lies outside the inputs and what the role's lanes
    let it read beside them, or None where the call goes on."""
    if call.tool not in ("Read", "Grep"):
        return None
    path = lanes.called_path(call) or ""
    if lanes.under(path, given["input"] + list(context.readable)):
        return None
    return f"The call reads {path}."
