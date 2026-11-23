"""Decides how a Claude Code session's end reads: finished, stopped by the usage limit until its
reset, or failed, from what `claude` printed."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Union

from session.claude import Output


@dataclass(frozen=True)
class Finished:
    """A session that ended with its answer: its reply's text and its session's ID."""

    reply: str
    session: str


@dataclass(frozen=True)
class Limited:
    """A session that the usage limit stopped: its reply's text so far, its session's ID, and the
    moment the limit resets."""

    reply: str
    session: str
    reset: datetime


@dataclass(frozen=True)
class Failed:
    """A session that ended without its answer: its reply's text so far, its session's ID where it
    got one, and why it failed."""

    reply: str
    session: str | None
    why: str


Ended = Union[Finished, Limited, Failed]


def ending(output: Output, now: datetime) -> Ended:
    """How the session that gave the output ended.

    Takes: what `claude` gave, and the moment it ended at.
    Gives: Limited, with the reset that the output names, where the usage limit stopped it;
    Finished where it answered; Failed with why otherwise.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("session.ending.ending")
