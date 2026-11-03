"""The lanes lane lays, one module each holding its action and its wording, as docs/lanes.md writes
them, whether its check rests on the calls kept, and its check; the sentences lane lays from the
routes, follow_routes' on the orchestrator's step and the result command on a subagent's last step,
as docs/routes.md writes them; and the sentence of each, made from its wording with what it takes,
which the step says and the guard tells, so the two never differ.

A lane's places are the `<...>` its wording shows, in order. Its takes fill them in that order, one
in each place but the last, which takes the rest, so a lane of one place takes all in it.

A lane checked as a call is made gives `allows(value, takes, root, cwd)`: whether the call's value,
the field of its input the lane judges, goes through, given what the lane takes in its first place,
the plugin's folder and the folder the call is made in. A lane checked as the subagent gives its
result gives `missing(given, done)`: what of its work is missing, given its places' texts and what
the subagent did, "" where nothing is."""

from __future__ import annotations

import re
from typing import Any

from lanes import (
    end_when,
    every_item,
    follow_routes,
    hold,
    in_form,
    read_only,
    read_whole,
    run_only,
    test_after,
    write_only,
)

LANES = {
    "read_only": read_only,
    "read_whole": read_whole,
    "write_only": write_only,
    "in_form": in_form,
    "run_only": run_only,
    "hold": hold,
    "test_after": test_after,
    "end_when": end_when,
    "every_item": every_item,
}
# The check of each lane checked as the subagent gives its result.
END = {
    "read_whole": read_whole.missing,
    "test_after": test_after.missing,
    "end_when": end_when.missing,
    "every_item": every_item.missing,
}
# The sentences laid from the routes, each by the name a step's lanes give it, with its action and
# wording; follow_routes lays and checks both.
ROUTED = {
    "follow_routes": (follow_routes.ACTION, follow_routes.WORDING),
    "result": ("end", follow_routes.RESULT),
}
# Where a wording shows what the lane takes, in quotes, by the name of its place.
TAKEN = re.compile(r"`<([a-z]+)>`")


def action(lane: str) -> str:
    """The action the lane, or the sentence laid from the routes, watches."""
    return ROUTED[lane][0] if lane in ROUTED else LANES[lane].ACTION


def hook(lane: str) -> str:
    """The hook that checks the lane: its own, or follow_routes for a sentence laid from the
    routes."""
    return "follow_routes" if lane in ROUTED else lane


def wording(lane: str) -> str:
    """The lane's wording, or that of the sentence laid from the routes."""
    return ROUTED[lane][1] if lane in ROUTED else LANES[lane].WORDING


def places(lane: str) -> list[str]:
    """The names of the lane's places, in the order its wording shows them."""
    return TAKEN.findall(wording(lane))


def placed(lane: str, takes: list[str]) -> dict[str, list[str]]:
    """The takes in the lane's places: one in each place but the last, the rest in the last; a
    place no take is left for holds none."""
    names = places(lane)
    found = {n: takes[at : at + 1] for at, n in enumerate(names[:-1])}
    return {**found, **({names[-1]: takes[len(names) - 1 :]} if names else {})}


def ends(lane: str) -> bool:
    """Whether the lane is checked as the subagent gives its result."""
    return lane in END


def calls(lane: str) -> bool:
    """Whether the lane's check rests on the calls kept, as docs/lanes.md's table says."""
    return lane == "follow_routes" or (lane in LANES and LANES[lane].CALLS)


def given_in(lane: str) -> dict[str, Any]:
    """The lane's IN, the JSON Schema docs/lanes.md gives what the lane is given: one or more texts
    in each of its places, and the calls kept where its check rests on them."""
    texts = {"type": "array", "items": {"type": "string"}, "minItems": 1}
    names = places(lane)
    takes = {
        "type": "object",
        "required": names,
        "additionalProperties": False,
        "properties": {n: texts for n in names},
    }
    return {
        "type": "object",
        "required": ["takes", "calls"] if calls(lane) else ["takes"],
        "additionalProperties": False,
        "properties": {"takes": takes, "calls": {"type": "array"}},
    }


def listed(takes: list[str]) -> str:
    """The things, each in quotes of its own, listed with commas and `or` before the last."""
    quoted = [f"`{t}`" for t in takes]
    return " or ".join(filter(None, [", ".join(quoted[:-1]), quoted[-1]]))


def sentence(lane: str, takes: list[str]) -> str:
    """The lane's sentence: its wording with the things in each place in quotes of their own,
    listed with commas and `or` before the last; its wording alone where it takes nothing."""
    if not takes:
        return wording(lane)
    found = placed(lane, takes)
    # Given as a function, the text put in is taken as it is, a backslash in it among the rest.
    return TAKEN.sub(lambda m: listed(found[m[1]]) if found[m[1]] else "", wording(lane))
