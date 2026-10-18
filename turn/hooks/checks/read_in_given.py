"""turn's agents read what their run was given alone, so the work is made and judged from what the
calling AI decided, not from what it did not give; the first user and the evaluator read what
the receiver has alone, as the receiver would, and the learner what the roles did."""

import os
import shlex
from typing import Any

import agents

TOOLS = {"Read": "file_path", "Grep": "path", "Glob": "path"}
OPERATORS = {";", "|", "||", "&", "&&", ">", ">>", "<", "<<", "(", ")", "`"}


def check(event: dict[str, Any]) -> list[str]:
    tool = event["tool_name"]
    role = agents.role(event)
    if role is None or tool not in (*TOOLS, "Bash"):
        return []
    kept = agents.running(event)
    if kept is None:
        return []
    if role in ("up", "generator"):
        given = kept["given"]
    elif role == "learner":
        given = kept["records"]
    else:
        given = kept["shown"]
    cwd = os.path.realpath(event["cwd"])
    places = [os.path.join(cwd, p) for p in given] + [agents.TURN]
    if tool == "Bash":
        # A command reads through the paths it names; one in the repository and outside what the
        # run was given is a read of it, while the repository's top is where the command runs.
        # Where the run is kept holds every role's prompt and reply, so the orchestrator alone,
        # which records its reading there, reads it; git reads the history of every file.
        if role == "up":
            places.append(os.path.join(cwd, kept["call"]["result"]))
        said = words(event)
        # A role takes what it is given from turn's script, naming where the run is kept, in a
        # command of that alone.
        command = str(event["tool_input"].get("command", ""))
        if role != "up" and agents.runs(command, "given") and not OPERATORS & set(said):
            return []
        named = [os.path.realpath(os.path.join(cwd, w)) for w in said]
        inside = [p for p in named if within(p, [cwd]) and p != cwd and os.path.exists(p)]
        if "git" not in said and all(within(p, places) for p in inside):
            return []
    else:
        path = event["tool_input"].get(TOOLS[tool])
        if path and within(os.path.realpath(os.path.join(cwd, path)), places):
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
