"""The generator writes the work alone, so the CCS, the checklists and the rest of the repository stay
as the calling AI left them, and the work is what the generator made of them."""

import os
from typing import Any

import agents
import shell


def check(event: dict[str, Any]) -> list[str]:
    role = agents.role(event)
    tool = event["tool_name"]
    if role is None or tool not in ("Write", "Edit", "Bash"):
        return []
    kept = agents.running(event)
    if kept is None:
        return []
    cwd = os.path.realpath(event["cwd"])
    if tool == "Bash":
        # A command may write outside the repository, such as in a folder of its own to run what
        # the work gives.
        command = str(event["tool_input"].get("command", ""))
        paths = [p for p in shell.written(command, cwd) if p.startswith(cwd + os.sep)]
    else:
        paths = [os.path.realpath(os.path.join(cwd, event["tool_input"].get("file_path", "")))]
    work = [os.path.join(cwd, w) for w in kept["work"]]
    if all(role == "generator" and p in work for p in paths):
        return []
    work = ", ".join(kept["work"])
    return [
        f"the generator alone writes, and the work alone: {work}; you give your part in your reply"
    ]
