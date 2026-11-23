"""Decides how a queue's runs lie on disk: the layout of `runs.json`, by `runs.schema.json` beside
this file."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from stacker.queue_file import Task

# The form of a queue's runs' file, in this folder.
SCHEMA = "runs.schema.json"

State = Literal["waiting for the start", "running", "waiting for the limit", "finished", "given up"]


@dataclass(frozen=True)
class Wait:
    """One wait for the usage limit: when the limit stopped the task, and when it went on, or None
    while it waits."""

    stopped: datetime
    went_on: datetime | None


@dataclass(frozen=True)
class Run:
    """How far a task got: where it stands, its Claude Code session from its first start, how many
    times the limit stopped it since it was last stacked, each wait for the limit, the moment it
    goes on while it waits, the moment it ended, and why it was given up."""

    state: State
    session: str | None
    stops: int
    waits: tuple[Wait, ...]
    until: datetime | None
    ended: datetime | None
    why: str | None


@dataclass(frozen=True)
class Kept:
    """A stacked task with its run."""

    task: Task
    run: Run


def load(path: str) -> tuple[Kept, ...] | None:
    """The runs that the file at `path` holds.

    Takes: the absolute path of a queue's `runs.json`.
    Gives: each task with its run, in the queue's order; None where no such file is there.
    Changes: nothing.
    Refuses: ValueError, naming the file and what's wrong, where it isn't JSON or leaves
    `runs.schema.json`.
    """
    raise NotImplementedError("record.runs.load")


def dump(kept: tuple[Kept, ...]) -> str:
    """The text of `runs.json` that holds each task with its run.

    Takes: each task with its run, in the queue's order.
    Gives: the text, in the form of `runs.schema.json`.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("record.runs.dump")
