"""The lanes lane lays, one module each holding its action, its wording as lane's docs/lanes.md
writes it, the tools it watches and its check; and the sentence of each, made from its wording with
what it takes, which a subagent's step says and the guard tells it.

A lane is held on a tool call, the PreToolUse event, or, where its module names the events, on the
subagent about to end, the SubagentStop event, or on both. A lane's check, `drifts(call, takes,
root)`, is given the call, or how the subagent ends, what the lane takes and the plugin's folder,
where a lane finds a file of the plugin it takes, such as in_form's form; it gives whether the call
drifts, or, where it says more than the sentence, the point it drifts by, "" for none. A lane's
module may name, beside its action, wording and check, the events it is held on, how many of the
things it takes its sentence shows, and the most things it takes; and give `beside(laid, root)`,
what it takes beside what its step names, from every lane laid in the subagent, as the guard calls
it, and `refused(takes, root)`, why it cannot be laid taking these, "" where it can, as the layer
calls it laying the lane and the guard on each run, where it is an error; RECORD, where its check
rests on what the subagent did before, read from its record, as every lane held at the subagent's
end does; and PORT, the port it reads a plugin's text at, as ports.py defines them, its check then
given, fourth, what reads that port.

What a lane's check is given is held first to the lane's IN, a JSON Schema `given_in` makes: the
texts put in each place of its sentence, and its subagent's record where its check rests on it; the
layer holds the things a proposal's lane takes to it, and the guard what each lane is given on a
run, so a lane's check meets only what it can check."""

from __future__ import annotations

import re
from typing import Any

import schema

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
# Where a wording shows what the lane takes, in quotes, and the name of the place.
TAKEN = re.compile(r"`<([a-z]+)>`")
# What each place of a lane's sentence is given: the texts put in it, one or more.
TEXTS = {"type": "array", "items": {"type": "string"}, "minItems": 1}


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
    """Whether the lane takes so many things: its IN holding them put in the places of its
    sentence, one or more in each, and no more than the most its module names, where it names one;
    so the layer, laying them, and the guard, reading them laid, hold them to the IN the guard holds
    a run's to."""
    held = given_in(lane)["properties"]["takes"]
    out = schema.held(held, dict(zip(places(lane), placed(lane, takes))))
    return out is None and len(takes) <= getattr(LANES[lane], "MOST", len(takes))


def places(lane: str) -> list[str]:
    """The name of each place the things the lane takes are put in, as its wording names them, such
    as `output` and `form`; of a lane that holds more than it shows, such as wait_for, those of the
    things it shows, and `held` for the rest."""
    named = TAKEN.findall(LANES[lane].WORDING)
    showing = shown(lane)
    return named if showing is None else [*named[:showing], "held"]


def placed(lane: str, takes: list[str]) -> list[list[str]]:
    """The things the lane takes, put in the places of its sentence, as `places` names them, in
    order: one in each of the first `alone` places, and the rest in the last."""
    first = alone(lane)
    return [*([t] for t in takes[:first]), takes[first:]]


def on_record(lane: str) -> bool:
    """Whether the lane's check rests on its subagent's record: its module says so, or it is held
    at the subagent's end."""
    return getattr(LANES[lane], "RECORD", False) or "SubagentStop" in held_on(lane)


def given_in(lane: str) -> dict[str, Any]:
    """The lane's IN, the JSON Schema of what its check is given: `takes`, the texts put in each
    place of its sentence, one or more each, and, where its check rests on its subagent's record,
    `record`, the record's entries."""
    named = places(lane)
    takes = {
        "type": "object",
        "required": named,
        "additionalProperties": False,
        "properties": dict.fromkeys(named, TEXTS),
    }
    record = ["record"] if on_record(lane) else []
    return {
        "type": "object",
        "required": ["takes", *record],
        "additionalProperties": False,
        "properties": {"takes": takes, "record": {"type": "array"}},
    }
