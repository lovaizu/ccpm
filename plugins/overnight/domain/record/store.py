"""Decides how each part reads and writes a queue's runs and replies: each write made whole before
any part reads it, and one write at a time among a runner's tasks."""

from __future__ import annotations

from contextlib import AbstractContextManager
from dataclasses import dataclass

from record.replies import Reply
from record.runs import Kept, Run
from stacker.queue_file import Queue, Task


@dataclass(frozen=True)
class Stood:
    """Where one stacked task stands: the task, its run, and the absolute path of its reply file."""

    task: Task
    run: Run
    reply: str


@dataclass(frozen=True)
class Standing:
    """Where a queue's tasks stand: whether its runner still carries them, and each task, in the
    queue's order."""

    carried: bool
    tasks: tuple[Stood, ...]


class NotStacked(Exception):
    """A queue that was never stacked, as overnight keeps nothing for it."""


def standing(queue_file: str) -> Standing:
    """Where the tasks of the queue at the absolute path `queue_file` stand.

    Takes: the queue file's path.
    Gives: each task with its run and where its reply lies, and whether a runner holds the queue's
    lock.
    Changes: where no runner holds the lock, gives up each task that hadn't ended, by
    `record.stopped.left`, and writes it.
    Refuses: NotStacked where overnight keeps nothing for the queue; ValueError where its runs'
    file leaves its form.
    """
    raise NotImplementedError("record.store.standing")


def stack(queue: Queue) -> tuple[Kept, ...]:
    """The queue's tasks written for its runner to carry.

    Takes: the queue, whose runner doesn't carry it.
    Gives: each task that didn't finish, with its run as written, which holds the session it goes
    on in, in the queue's order.
    Changes: writes each such task with its run waiting for the start, its session kept and its
    stops counted from zero, by `record.stopped.carried_on`, and leaves each finished task as it
    ended.
    Refuses: OSError where the queue's folder can't be written.
    """
    raise NotImplementedError("record.store.stack")


def hold(queue_file: str) -> AbstractContextManager[None]:
    """The queue's lock, held while the runner carries its tasks.

    Takes: the queue file's absolute path.
    Gives: a context that holds the lock until it exits, or until the runner ends however it ends.
    Changes: makes the lock's file where none is there.
    Refuses: record.lock.Held where another runner holds it.
    """
    raise NotImplementedError("record.store.hold")


def mark(queue_file: str, task: str, run: Run) -> None:
    """Writes the run of the task, by its name, in place of the one kept.

    Takes: the queue file's absolute path, the task's name, and its run as it now stands.
    Gives: nothing.
    Changes: the queue's runs, written whole before any part reads them.
    Refuses: KeyError where the queue keeps no task of that name.
    """
    raise NotImplementedError("record.store.mark")


def add_reply(queue_file: str, task: str, reply: Reply) -> None:
    """Adds the reply at the end of the task's reply file.

    Takes: the queue file's absolute path, the task's name, and what its session answered.
    Gives: nothing.
    Changes: the task's reply file, which gets the reply after its earlier parts, with the line of
    the run's last wait before it where the limit stopped the part before.
    Refuses: KeyError where the queue keeps no task of that name.
    """
    raise NotImplementedError("record.store.add_reply")
