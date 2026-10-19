"""turn's agents read what their run was given alone, so the work is made and judged from what the
calling AI decided, not from what it did not give; the orchestrator reads the work only to decide,
as its reading between would find the Good the work meant; the first user and the evaluator read
what the receiver has alone, as the receiver would, and the learner what the roles did."""

import os
import shlex
from typing import Any

import agents
import run

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
OPERATORS = {";", "|", "||", "&", "&&", ">", ">>", "<", "<<", "(", ")", "`"}


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
    places = [os.path.join(cwd, p) for p in given] + [agents.TURN]
    if tool in TOOLS:
        path = event["tool_input"].get(TOOLS[tool])
        if path and within(os.path.realpath(os.path.join(cwd, path)), places):
            return []
    else:
        # A command reads through the paths it names; one in the repository and outside what the
        # run was given is a read of it, the repository's top too, as it holds all, but where cd
        # goes, as that reads nothing.
        # Where the run is kept holds every role's prompt and reply, so the orchestrator alone,
        # which records its reading there, reads it; git reads the history of every file.
        orchestrator = role in KEEPS
        if orchestrator:
            places.append(os.path.join(cwd, kept["call"]["result"]))
        said = words(event)
        # A role takes what it is given, the parts of the work, and the learner each record, from
        # turn's script, naming where the run is kept, in a command of that alone.
        command = str(event["tool_input"].get("command", ""))
        asks = any(agents.runs(command, c) for c in ("given", "parts", "record"))
        if not orchestrator and asks and not OPERATORS & set(said):
            return []
        named = [
            os.path.realpath(os.path.join(cwd, w))
            for i, w in enumerate(said)
            if not (i and said[i - 1] == "cd")
        ]
        inside = [p for p in named if within(p, [cwd]) and os.path.exists(p)]
        if "git" not in said and all(within(p, places) for p in inside):
            return []
    return [f"read what you were given alone: {', '.join(given)} and turn's own files"]


def words(event: dict[str, Any]) -> list[str]:
    """The command's words, with `;`, `|`, `&&` and the like apart from the paths they follow."""
    command = str(event["tool_input"].get("command", ""))
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        return list(lexer)
    except ValueError:
        return command.split()


def within(path: str, places: list[str]) -> bool:
    return any(path == p or path.startswith(p + os.sep) for p in places)
