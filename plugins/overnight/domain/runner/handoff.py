"""Decides the form in which a stacked queue reaches its runner's program, on its standard input."""

from __future__ import annotations

from dataclasses import dataclass

from stacker.queue_file import Task


@dataclass(frozen=True)
class Carried:
    """A task that the runner carries, with the session it goes on in, or None where it starts
    anew."""

    task: Task
    session: str | None


@dataclass(frozen=True)
class Handoff:
    """What the stacker hands its runner, so that the runner starts with no read of the record: the
    queue file's absolute path, the queue's start as `HH:MM`, or None for at once, and each task it
    carries, in the queue's order."""

    queue_file: str
    start: str | None
    tasks: tuple[Carried, ...]


def encode(handoff: Handoff) -> str:
    """The text that hands the runner the queue.

    Takes: what the stacker hands the runner.
    Gives: the text that `decode` reads back to it.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("runner.handoff.encode")


def decode(text: str) -> Handoff:
    """What `encode` gave the text of.

    Takes: the text of the runner's standard input.
    Gives: the queue file's path, the queue's start, and each task with its session.
    Changes: nothing.
    Refuses: ValueError, saying what's wrong, where the text isn't what `encode` gives.
    """
    raise NotImplementedError("runner.handoff.decode")
