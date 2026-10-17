"""turn's agents read what their run was given alone, so the work is made and judged from what the
calling AI decided, not from what it did not give, and the first user and the evaluator read what
the receiver has alone, as the receiver would."""

import os
import shlex
from typing import Any

import agents

TOOLS = {"Read": "file_path", "Grep": "path", "Glob": "path"}


def check(event: dict[str, Any]) -> list[str]:
    tool = event["tool_name"]
    role = agents.role(event)
    if role is None or tool not in (*TOOLS, "Bash"):
        return []
    kept = agents.running(event)
    if kept is None:
        return []
    given = kept["given"] if role in ("up", "generator") else kept["shown"]
    cwd = os.path.realpath(event["cwd"])
    places = [os.path.join(cwd, p) for p in given] + [agents.TURN]
    if tool == "Bash":
        # A command reads through the paths it names; one in the repository and outside what the
        # run was given is a read of it, while the repository's top is where the command runs and
        # the result is where the orchestrator records its reading.
        places.append(os.path.join(cwd, kept["call"]["result"]))
        named = [os.path.realpath(os.path.join(cwd, w)) for w in words(event)]
        inside = [p for p in named if within(p, [cwd]) and p != cwd and os.path.exists(p)]
        if all(within(p, places) for p in inside):
            return []
    else:
        path = event["tool_input"].get(TOOLS[tool])
        if path and within(os.path.realpath(os.path.join(cwd, path)), places):
            return []
    return [f"read what you were given alone: {', '.join(given)} and turn's own files"]


def words(event: dict[str, Any]) -> list[str]:
    command = str(event["tool_input"].get("command", ""))
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()


def within(path: str, places: list[str]) -> bool:
    return any(path == p or path.startswith(p + os.sep) for p in places)
