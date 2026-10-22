"""A tool call read as one action of a subagent's steps, the one a lane watches: begin, read, write,
run, test, hand on, wait or end. A Bash call is a run, of each command it runs; a call of a tool no
lane of this version reads is no action."""

from __future__ import annotations

from typing import Any, NamedTuple

import shell


class Call(NamedTuple):
    """The action a call is, "" for none a lane watches, and what it acts on: for a run, each
    command, as its words."""

    action: str
    what: list[list[str]]


def read(event: dict[str, Any]) -> Call:
    """The call of the PreToolUse event, read as its action."""
    if event["tool_name"] != "Bash":
        return Call("", [])
    command = str(event["tool_input"].get("command", ""))
    return Call("run", list(runs(command, event["cwd"])))


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
