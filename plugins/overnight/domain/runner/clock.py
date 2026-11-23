"""Decides how overnight reads the time and waits for a moment, the one place where a test puts a
double of the computer's clock, which each part that reads the time goes through."""

from __future__ import annotations

from datetime import datetime


def now() -> datetime:
    """The moment it is, on the computer's clock, with its offset from UTC.

    Takes: nothing.
    Gives: the moment.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("runner.clock.now")


def sleep_until(moment: datetime) -> None:
    """Waits until the moment.

    Takes: the moment, with its offset from UTC.
    Gives: nothing, at the moment, or at once where it has passed.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("runner.clock.sleep_until")
