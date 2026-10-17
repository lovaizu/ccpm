"""turn's agents read what their run was given alone, so the work is made and judged from what the
calling AI decided, not from what it did not give."""

import os
from typing import Any

import agents

TOOLS = {"Read": "file_path", "Grep": "path", "Glob": "path"}


def check(event: dict[str, Any]) -> list[str]:
    if agents.role(event) not in ("up", "generator") or event["tool_name"] not in TOOLS:
        return []
    kept = agents.running(event)
    if kept is None:
        return []
    cwd = os.path.realpath(event["cwd"])
    path = event["tool_input"].get(TOOLS[event["tool_name"]])
    places = [os.path.join(cwd, p) for p in kept["given"]] + [agents.TURN]
    if path and within(os.path.realpath(os.path.join(cwd, path)), places):
        return []
    return [f"read what the run was given alone: {', '.join(kept['given'])} and turn's own files"]


def within(path: str, places: list[str]) -> bool:
    return any(path == p or path.startswith(p + os.sep) for p in places)
