"""A tool call read as one action of a subagent's steps, the one a lane watches: begin, read, write,
run, test, hand on, wait or end. A Bash call is a run, of each command it runs, writing what they
write; a call of a tool that writes a file is a write of it; a call of a tool no lane of this version
reads is no action."""

from __future__ import annotations

import os
from typing import Any, NamedTuple

import shell

# The tools that write a file, each with the field of its input that names it.
WRITERS = {"Write": "file_path", "Edit": "file_path", "NotebookEdit": "notebook_path"}


class Call(NamedTuple):
    """The action a call is, "" for none a lane watches, and what it acts on: for a run, each
    command, as its words; and each file it writes, as its whole path."""

    action: str
    what: list[list[str]]
    written: tuple[str, ...] = ()


def read(event: dict[str, Any]) -> Call:
    """The call of the PreToolUse event, read as its action."""
    if event["tool_name"] in WRITERS:
        named = str(event["tool_input"].get(WRITERS[event["tool_name"]], ""))
        # A path is named from the folder the call is made in, as the tool takes it.
        file = os.path.realpath(os.path.join(event["cwd"], named))
        return Call("write", [], (file,) if named else ())
    if event["tool_name"] != "Bash":
        return Call("", [])
    command = str(event["tool_input"].get("command", ""))
    written = tuple(shell.written(command, event["cwd"]))
    return Call("run", list(runs(command, event["cwd"])), written)


def runs(command: str, cwd: str) -> list[list[str]]:
    """Each command the shell command runs, in order, as its words, in the forms the steps tell and
    the AI writes: a cd is no command, a redirect and its target are no words, and git's own
    options before its command are left out, so `git -C notes commit` runs `git commit`."""
    found = []
    for here, said, _ in shell.statements(command, cwd):
        words = shell.without_redirects(said)
        if words[:1] == ["git"]:
            words = ["git", *shell.git_statement(here, words)[1]]
        found.append(words)
    return found
