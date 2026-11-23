"""Decides how overnight runs the program `claude`, the one place where a test puts a double of
Claude Code."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Output:
    """What a run of `claude` gave: its exit code, its standard output, and its standard error."""

    code: int
    out: str
    err: str


def claude(arguments: Sequence[str], cwd: str) -> Output:
    """What `claude` gives with the arguments, run in the folder `cwd`.

    Takes: the arguments after `claude`, and the absolute path of the folder it runs in.
    Gives: its exit code and what it printed, once it ends.
    Changes: whatever the session does, within what the arguments allow it.
    Refuses: FileNotFoundError where no `claude` is on the path.
    """
    raise NotImplementedError("session.claude.claude")
