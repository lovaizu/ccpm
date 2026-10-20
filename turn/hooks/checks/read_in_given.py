"""turn's agents read what their run was given alone, so the work is made and judged from what the
calling AI decided, not from what it did not give; the orchestrator reads the work only to decide,
as its reading between would find the Good the work meant; the first user and the evaluator read
what the receiver has alone, as the receiver would, and the learner what the roles did."""

import os
from typing import Any

import agents
import run
import shell

TOOLS = {"Read": "file_path", "Grep": "path", "Glob": "path"}
# What each agent may read: the generator, what the run was given, and the orchestrator too, but the
# work until it decides; the first user and the evaluator, what the receiver has; the learner, the
# records it is shown.
GIVEN = {
    "up": lambda kept: [p for p in kept["given"] if "decide" in kept or p not in kept["work"]],
    "generator": lambda kept: kept["given"],
    "first-user": lambda kept: kept["shown"],
    "evaluator": lambda kept: kept["shown"],
    "learner": run.learnt_from,
}
# The agent that records its readings where the run is kept, and so reads it.
KEEPS = ("up",)


def check(event: dict[str, Any]) -> list[str]:
    tool = event["tool_name"]
    role = agents.role(event)
    if role is None or tool not in (*TOOLS, "Bash"):
        return []
    kept = agents.running(event)
    if kept is None:
        return []
    given = GIVEN[role](kept)
    cwd = os.path.realpath(event["cwd"])
    places = [os.path.realpath(os.path.join(cwd, p)) for p in given] + [agents.TURN]
    if tool in TOOLS:
        path = event["tool_input"].get(TOOLS[tool])
        if path and within(os.path.realpath(os.path.join(cwd, path)), places):
            return []
    else:
        # A command reads through the paths it names; one in the repository and outside what the
        # run was given is a read of it, the repository's top too, as it holds all. Where the run is
        # kept holds every role's prompt and reply, so the orchestrator alone, which records its
        # reading there, reads it, and a role names it only for turn's script to show its part;
        # git run in the repository reads the history of every file.
        if role in KEEPS:
            places.append(os.path.realpath(os.path.join(cwd, kept["call"]["result"])))
        command = str(event["tool_input"].get("command", ""))
        inside = [p for p in shell.named(command, cwd) if within(p, [cwd]) and os.path.exists(p)]
        history = any(shell.inside(folder, cwd) for folder, _ in shell.git(command, cwd))
        if not history and all(within(p, places) for p in inside):
            return []
    return [f"read what you were given alone: {', '.join(given)} and turn's own files"]


def within(path: str, places: list[str]) -> bool:
    return any(path == p or path.startswith(p + os.sep) for p in places)
