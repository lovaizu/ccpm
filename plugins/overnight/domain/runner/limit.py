"""Decides how a task waits at the usage limit: when it goes on after the reset, and at which stop
it's given up."""

from __future__ import annotations

from datetime import datetime


def resume_at(reset: datetime, stops: int) -> datetime | None:
    """When a task that the limit stopped goes on.

    Takes: the moment the limit resets, and how many times the limit has stopped the task since it
    was last stacked, this stop included.
    Gives: two minutes after the reset; None at the seventh stop, where the task is given up.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("runner.limit.resume_at")
