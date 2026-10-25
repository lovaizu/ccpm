"""The lanes lane lays, one module each holding its action, its wording as lane's docs/lanes.md writes
it, the tools it watches and its check; and the sentence of each, made from its wording with what it
takes, which a subagent's step says and the guard tells it.

A lane is held on a tool call, the PreToolUse event, or, where its module names the events, on the
subagent about to end, the SubagentStop event, or on both. A lane's check, `drifts(call, takes,
root)`, is given the call, or how the subagent ends, what the lane takes and the plugin's folder,
where a lane finds a file of the plugin it takes, such as in_form's form; it gives whether the call
drifts, or, where it says more than the sentence, the point it drifts by, "" for none. A lane's
module may name, beside its action, wording and check, the events it is held on, how many of the
things it takes its sentence shows, and the most things it takes."""

from __future__ import annotations

import re

from lanes import (
    as_printed,
    end_when,
    every_item,
    follow_next,
    hands_off,
    in_form,
    read_only,
    read_whole,
    start_with,
    test_after,
    wait_for,
    write_only,
)

LANES = {
    "start_with": start_with,
    "read_only": read_only,
    "read_whole": read_whole,
    "write_only": write_only,
    "in_form": in_form,
    "hands_off": hands_off,
    "test_after": test_after,
    "as_printed": as_printed,
    "follow_next": follow_next,
    "wait_for": wait_for,
    "end_when": end_when,
    "every_item": every_item,
}
# Where a wording shows what the lane takes, in quotes.
TAKEN = re.compile(r"`<[a-z]+>`")


def held_on(lane: str) -> tuple[str, ...]:
    """The events the lane is held on: those its module names, PreToolUse alone where it names
    none."""
    return getattr(LANES[lane], "EVENTS", ("PreToolUse",))


def slots(lane: str) -> int:
    """How many places the lane's wording shows for what it takes."""
    return len(TAKEN.findall(LANES[lane].WORDING))


def shown(lane: str) -> int | None:
    """How many of the things the lane takes its sentence shows, None for all."""
    return getattr(LANES[lane], "SHOWN", None)


def sentence(lane: str, takes: list[str]) -> str:
    """The lane's sentence: its wording with the things it shows put in, one in each place in order,
    the last place taking the rest, each thing in quotes of its own, listed with commas and `or`
    before the last; of a lane that holds more than it shows, such as wait_for, the things it shows
    alone."""
    last, showing = slots(lane) - 1, takes[: shown(lane)]
    parts = iter([*([t] for t in showing[:last]), showing[last:]])

    def listed(_: re.Match[str]) -> str:
        quoted = [f"`{t}`" for t in next(parts)]
        return " or ".join(filter(None, [", ".join(quoted[:-1]), quoted[-1]]))

    # Given as a function, the text put in is taken as it is, a backslash in it among the rest.
    return TAKEN.sub(listed, LANES[lane].WORDING)


def alone(lane: str) -> int:
    """How many of the first things the lane takes stand each alone in a place of its sentence:
    those before its last place, which takes the rest; of a lane that holds more than it shows,
    such as wait_for, the things it shows."""
    showing = shown(lane)
    return slots(lane) - 1 if showing is None else showing


def fits(lane: str, takes: list[str]) -> bool:
    """Whether the lane takes so many things: one or more for each place its wording shows, the last
    taking the rest; of a lane that holds more than it shows, one or more after those it shows; and
    no more than the most its module names, where it names one."""
    showing, most = shown(lane), getattr(LANES[lane], "MOST", len(takes))
    least = slots(lane) if showing is None else showing + 1
    return least <= len(takes) <= most
