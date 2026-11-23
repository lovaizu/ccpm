"""Decides which queue can be taken in: each fault that keeps one of its tasks from starting, and
how the user mends the queue for it."""

from __future__ import annotations

from record.store import Standing
from stacker.queue_file import Fault, Queue


def faults(queue: Queue, standing: Standing | None, sandbox_holds: bool) -> tuple[Fault, ...]:
    """Each fault that keeps a task of the queue from starting.

    Takes: the queue, where its tasks stand, or None where the queue was never stacked, and whether
    Claude Code's sandbox can hold a task's commands to its dir on this computer.
    Gives: a fault with its mend for each task whose prompt's file or dir isn't there, for each task
    that writes where the sandbox can't hold it, and one for a queue whose runner still carries it,
    with where its tasks stand; none where each task can start.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("stacker.admission.faults")
