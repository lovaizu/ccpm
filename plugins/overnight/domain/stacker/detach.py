"""Decides how a queue's runner outlives the session that starts it, on each OS that Claude Code
runs on."""

from __future__ import annotations

from runner.handoff import Handoff


class CantStart(Exception):
    """A runner that the OS didn't start, with what the OS said."""


def start_runner(handoff: Handoff) -> None:
    """Starts the queue's runner as a program apart from Claude Code.

    Takes: what the runner is handed: the queue file's absolute path, the queue's start, and each
    task it carries with its session.
    Gives: nothing.
    Changes: starts `queue.py run` apart from the session that runs the stacker, with the handoff
    on its standard input by `runner.handoff.encode`, so that it goes on after that session ends.
    Refuses: CantStart where the OS doesn't start it.
    """
    raise NotImplementedError("stacker.detach.start_runner")
