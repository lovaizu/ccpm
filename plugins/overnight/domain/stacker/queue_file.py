"""Decides how a queue file that the user writes reads as a queue, by its form in
`queue.schema.json` beside this file."""

from __future__ import annotations

from dataclasses import dataclass

# The form of a queue file, in this folder.
SCHEMA = "queue.schema.json"


@dataclass(frozen=True)
class Task:
    """One prompt to carry to its end in its folder: its name in the queue, the absolute path of
    its prompt's file, the absolute path of its folder, and whether the queue lets it write
    there."""

    name: str
    prompt: str
    dir: str
    writes: bool


@dataclass(frozen=True)
class Queue:
    """The tasks stacked together and the hour they start, as the user wrote them: the queue
    file's absolute path, its start as `HH:MM`, or None for at once, and each task in the order
    they start."""

    path: str
    start: str | None
    tasks: tuple[Task, ...]


@dataclass(frozen=True)
class Fault:
    """One reason that the queue can't be taken in, and how the user mends the queue file for it."""

    what: str
    mend: str


class Refused(Exception):
    """A queue not taken in, with each fault and its mend."""

    def __init__(self, faults: tuple[Fault, ...]):
        super().__init__("; ".join(each.what for each in faults))
        self.faults = faults


def read(path: str) -> Queue:
    """The queue that the queue file at `path` holds.

    Takes: the queue file's absolute path.
    Gives: the queue, each task's prompt made absolute from the queue file's folder, and each task
    that the file gives no `writes` one that may only read.
    Changes: nothing.
    Refuses: Refused, with each fault and its mend, where the file can't be read, isn't JSON,
    leaves `queue.schema.json`, or names a task twice.
    """
    raise NotImplementedError("stacker.queue_file.read")
