"""Decides how a runner's stop shows: a lock on its queue that the OS releases however the runner
ends."""

from __future__ import annotations

from contextlib import AbstractContextManager


class Held(Exception):
    """A lock that another runner holds."""


def hold(path: str) -> AbstractContextManager[None]:
    """The lock at the absolute path `path`, held while the `with` block runs.

    Takes: the lock's path.
    Gives: a context that holds the lock until it exits, or until the program ends however it ends.
    Changes: makes the lock's file where none is there.
    Refuses: Held where another program holds it.
    """
    raise NotImplementedError("record.lock.hold")


def held(path: str) -> bool:
    """Whether a program holds the lock.

    Takes: the lock's absolute path.
    Gives: True where a program holds it; False where none does, or no lock's file is there.
    Changes: nothing, as it asks without holding the lock.
    Refuses: nothing.
    """
    raise NotImplementedError("record.lock.held")
