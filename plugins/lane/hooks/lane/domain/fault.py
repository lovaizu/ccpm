"""Decides how a part of Lane says that it can't do what it was asked: why, and who must fix it, so
that no check passes what it didn't check, as the principle A stop gives the step back says."""

from __future__ import annotations


class Fault(Exception):
    """What a part of Lane could not read, run, or check: `why`, in words that whoever reads it can
    act on, and `who`, the one who must fix it, such as `the plugin's maker` or `Lane`."""

    def __init__(self, why: str, who: str) -> None:
        super().__init__(f"{why} ({who} must fix it)")
        self.why = why
        self.who = who
