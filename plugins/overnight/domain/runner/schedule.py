"""Decides when each task of a queue starts: in the queue's order, three at a time, from the
queue's start."""

from __future__ import annotations

from runner.handoff import Handoff

# How many tasks run at a time, so that a queue moves on while the usage window it shares lasts.
AT_A_TIME = 3


def carry(handoff: Handoff) -> None:
    """Carries each task of the queue to its end, with the queue's lock held.

    Takes: what the stacker handed the runner: the queue file's absolute path, the queue's start,
    and each task with the session it goes on in, in the queue's order.
    Gives: nothing, once each task has ended.
    Changes: holds the queue's lock while it runs, waits by `runner.clock` until the next moment
    that the computer's clock reads the start, or waits not at all without one, and then starts
    each task by `runner.task.carry`, three at a time, in the queue's order.
    Refuses: record.lock.Held where another runner carries the queue, starting no task.
    """
    raise NotImplementedError("runner.schedule.carry")
