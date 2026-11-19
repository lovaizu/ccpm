"""The form of what a plugin's order takes and gives, as starts_due.in.schema.json and
starts_due.out.schema.json beside this module give it: the run as the order sees it, which facts
of the run record it holds among them, and the starts due or the run's end."""

from __future__ import annotations

from typing import TypedDict

from record import Run


class OrderMove(TypedDict, total=False):
    """A move of the run as the plugin's order sees it: its `kind`, one of `command`, `start`, and
    `result`, and the `command` typed, or the `role` started, or the `role` and the `result` it
    gave."""

    kind: str
    command: str
    role: str
    result: str


class OrderRun(TypedDict):
    """The run as the plugin's order sees it: the skill that called it, the words typed after its
    command, and each of its moves in their order."""

    skill: str
    words: str
    moves: list[OrderMove]


class StartDue(TypedDict):
    """A role to start now, by its agent type, and how many times at once."""

    role: str
    count: int


class StartsDue(TypedDict, total=False):
    """What the plugin's order gives: the `starts` due now, none where the run waits, such as for
    the person's answer; or `ends`, true where the run ends."""

    starts: list[StartDue]
    ends: bool


def order_run(run: Run) -> OrderRun:
    """The run as the plugin's order sees it.

    Takes: the run as its record stands.
    Gives: its skill and words, and each command that called or moved it, each start made, and each
    result, in their order; a start whose Agent call failed, or that ended with no result, such as
    one stopped by TaskStop, is left out, so that the order gives its role due again.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("order.order_run")
