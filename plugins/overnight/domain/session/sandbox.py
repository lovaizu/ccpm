"""Decides whether Claude Code's sandbox can hold a task's commands to its dir on this computer."""

from __future__ import annotations


def can_hold() -> bool:
    """Whether a writing task can be held to its dir here.

    Takes: nothing.
    Gives: True where Claude Code's sandbox runs on this computer; False where it can't, such as on
    Windows outside WSL2.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("session.sandbox.can_hold")
