"""Decides how a task's session runs: its prompt read, `claude` run in the task's dir with what the
task may do, and the session's end told."""

from __future__ import annotations

from session.ending import Ended
from stacker.queue_file import Task


def run(task: Task, session: str | None) -> Ended:
    """The end of the task's session, run to its end.

    Takes: the task, and the session it goes on in, or None to start it anew, so that a start and a
    resume take this one call.
    Gives: Finished, Limited with the reset, or Failed with why, with the session's ID.
    Changes: whatever the session does, within what `session.permissions.arguments` allows it.
    Reads the time, which `session.ending.ending` takes, through `runner.clock`.
    Refuses: nothing, as each fault that ends the session, such as a prompt's file gone, is Failed.
    """
    raise NotImplementedError("session.session.run")
