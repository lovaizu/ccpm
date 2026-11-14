"""Decides whether a result is one that the role may give, as result.py asks it, and which Result a
run of result.py gave, as the guard asks it at the PostToolUse of that run, so that the guard goes
on only from a Result that a run of result.py gave, as the principle A result only from the result
script says."""

from __future__ import annotations

from collections.abc import Sequence

from domain.event import Event
from domain.laid_set import LaidSet
from domain.run_record import Result, Run


def may_give(laid_set: LaidSet, role: str) -> tuple[str, ...]:
    """Each result that the role may give, as its gives_result Lane takes them, in their order;
    none for a role of no such Lane."""
    raise NotImplementedError("results.may_give")


def given(event: Event, laid_set: LaidSet, runs: Sequence[Run]) -> Result | None:
    """The Result that a run of result.py gave, from the moment that tells it ran: a RAN of the
    command of the plugin's result.py, word for word with a role and a result, that gave 0. A
    subagent's Result is for the subagent of the moment's `agent_id`, of the Start that ties it;
    the main conversation's is for the skill it names, in the Run of that skill. None for any other
    moment, as for result.py at the end of a longer command, which gives no Result."""
    raise NotImplementedError("results.given")
