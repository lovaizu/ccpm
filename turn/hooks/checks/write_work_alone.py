"""The generator writes the work alone, so the CCS, the checklists and the rest of the repository stay
as the calling AI left them, and the work is what the generator made of them."""

import os
from typing import Any

import agents


def check(event: dict[str, Any]) -> list[str]:
    role = agents.role(event)
    if role is None or event["tool_name"] not in ("Write", "Edit"):
        return []
    kept = agents.running(event)
    if kept is None:
        return []
    cwd = os.path.realpath(event["cwd"])
    path = os.path.realpath(os.path.join(cwd, event["tool_input"].get("file_path", "")))
    if role == "generator" and path in [os.path.join(cwd, w) for w in kept["work"]]:
        return []
    work = ", ".join(kept["work"])
    return [
        f"the generator alone writes, and the work alone: {work}; you give your part in your reply"
    ]
