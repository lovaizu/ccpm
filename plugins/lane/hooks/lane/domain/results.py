"""Decides whether a result is one that the role may give, as result.py asks it, and which Result a
run of result.py gave, as the guard asks it at the PostToolUse of that run, so that the guard goes
on only from a Result that a run of result.py gave, as the principle A result only from the result
script says."""

from __future__ import annotations

from collections.abc import Sequence

from domain.event import COMMAND, RAN, Event
from domain.laid_set import LaidSet
from domain.run_record import Result, Run

# How the command of a plugin's result.py ends its second word, its script.
_SCRIPT = "/hooks/lane/result.py"


def may_give(laid_set: LaidSet, role: str) -> tuple[str, ...]:
    """Each result that the role may give, as its gives_result Lane takes them, in their order;
    none for a role of no such Lane."""
    return tuple(
        result
        for lane in laid_set.lanes
        if lane.role == role and lane.type == "gives_result"
        for result in lane.takes
    )


def given(event: Event, laid_set: LaidSet, runs: Sequence[Run]) -> Result | None:
    """The Result that a run of result.py gave, from the moment that tells it ran: a RAN of the
    command of the plugin's result.py, word for word with a role and a result, that gave 0. A
    subagent's Result is for the subagent of the moment's `agent_id`, of the Start that ties it;
    the main conversation's is for the skill it names, in the Run of that skill. None for any other
    moment, as for result.py at the end of a longer command, which gives no Result."""
    call = event.call
    if event.moment != RAN or event.failed or call is None or call.kind != COMMAND:
        return None
    words = call.command.split()
    if len(words) != 4 or words[0] != "python3" or not words[1].endswith(_SCRIPT):
        return None
    role, result = words[2], words[3]
    if result not in may_give(laid_set, role):
        return None
    if not event.agent:
        return Result(role, result) if role in laid_set.skills else None
    start = next((s for run in runs for s in reversed(run.starts) if s.agent == event.agent), None)
    if start is None or start.role != role:
        return None
    return Result(role, result, event.agent, start.number)
