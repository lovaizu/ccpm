"""The clock that the runner reads and waits on."""

from __future__ import annotations

from datetime import datetime


def now() -> datetime:
    """The time now, with its time zone.

    Takes: nothing.
    Gives: the time now.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("runner.clock.now")


def wait_until(when: datetime) -> None:
    """Waits until the time.

    Takes: a time with its time zone.
    Gives: nothing, once the clock reads the time or later, at once where it already does.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("runner.clock.wait_until")
