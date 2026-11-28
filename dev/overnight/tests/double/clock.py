"""The double of the clock and the sleep that overnight's code takes, for the cases that run it in
the test's own process: a clock that starts at 23:15 and moves on only by each wait."""

from __future__ import annotations

import datetime


class Clock:
    """A clock that starts at 23:15 and moves on only by each wait, keeping each wait in seconds."""

    def __init__(self) -> None:
        self.at = datetime.datetime(2026, 11, 28, 23, 15)
        self.waits: list[float] = []

    def now(self) -> datetime.datetime:
        return self.at

    def sleep(self, seconds: float) -> None:
        self.waits.append(seconds)
        self.at += datetime.timedelta(seconds=seconds)
