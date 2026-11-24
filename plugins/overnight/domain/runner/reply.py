"""What a reply of Claude Code says: how its run ended, the ID of its conversation, and when a
usage limit that stopped it resets."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Union

from runner.claude import Output


@dataclass(frozen=True)
class Limited:
    """A run that the usage limit stopped: its conversation, where the reply names one, and when
    the limit resets, where the reply tells it."""

    conversation: str | None
    resets: datetime | None


@dataclass(frozen=True)
class Failed:
    """A run that ended by an error of its own: the error, in Claude Code's words."""

    error: str


@dataclass(frozen=True)
class Ended:
    """A run whose conversation ended: its conversation and its last words."""

    conversation: str
    last_words: str


# Union, where the annotations write `|`, as Python runs this line, and Python 3.9 can't join
# classes by `|`.
Reply = Union[Limited, Failed, Ended]


def read(output: Output) -> Reply:
    """What the run's output says.

    Takes: what `claude.run` gave.
    Gives: Limited where the usage limit stopped the run, Ended where the conversation ended, and
    Failed where it ended by an error of its own or the output can't be read.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("runner.reply.read")
