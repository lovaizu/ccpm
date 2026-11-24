"""How the OS tells a runner's process apart from any later process with the same ID: by its ID
and its start time."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Runner:
    """A runner's process, as its OS tells it: its ID, and its start time in the OS's own words,
    which no later process with the same ID shares."""

    pid: int
    started: str


def identify(pid: int) -> Runner:
    """The process with the ID `pid`, as it runs now.

    Takes: the ID of a process that runs.
    Gives: its ID and its start time, as its OS tells them.
    Changes: nothing.
    Refuses: LookupError, naming the ID, where no process with the ID runs.
    """
    raise NotImplementedError("pieces.process.identify")


def runs(runner: Runner) -> bool:
    """Whether the runner's process still runs.

    Takes: a runner that `identify` gave.
    Gives: True where a process with its ID and its start time runs, and False where none does,
    such as when its ID now names a later process.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("pieces.process.runs")
