"""Decides what each end of a task's session leads to, so that whatever ends one task gives up only
that one."""

from __future__ import annotations

from runner.handoff import Carried


def carry(queue_file: str, carried: Carried) -> None:
    """Carries the task to its end.

    Takes: the queue file's absolute path, and the task with the session it goes on in, or None
    where it starts anew.
    Gives: nothing.
    Changes: the task's run and reply in the record: running, then, after each session's end, the
    reply added and the run marked finished, waiting for the limit until it goes on, or given up
    with why and its session; and the session resumed at each end of a wait.
    Refuses: nothing, as each fault, such as an error of the record, gives up the task with why, so
    that the queue's other tasks go on.
    """
    raise NotImplementedError("runner.task.carry")
