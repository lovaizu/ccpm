"""The lanes lane lays, one module each holding its action and its wording, as docs/lanes.md writes
them, whether its check rests on the calls kept, and its check; the sentences lane lays from the
routes, follow_routes' on the skill's step and the result command on a subagent's last step,
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
from typing import Any, NamedTuple

import schema

from lanes import (
    edit_only,
    end_when,
    every_item,
    follow_routes,
    hold,
    in_form,
    read_only,
    read_whole,
    run_only,
    run_step,
    test_after,
    write_only,
    write_step,
)

LANES = {
    "read_only": read_only,
    "read_whole": read_whole,
    "write_only": write_only,
    "write_step": write_step,
    "in_form": in_form,
    "edit_only": edit_only,
    "run_only": run_only,
    "run_step": run_step,
    "hold": hold,
    "test_after": test_after,
    "end_when": end_when,
    "every_item": every_item,
}
# The lanes of the trace kind, each naming the call that shows its step done, which the guard holds
# in the order of the steps, and at the end: each gives `traces(tool, value, given, done)`, whether
# a call is its trace, and `missing(given, done)`, what of its trace hasn't come back.
TRACE = {"read_whole": read_whole, "run_step": run_step, "write_step": write_step}
# The check of each lane checked as the subagent gives its result, beside the traces.
END = {
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
# Each wording lane laid before the current one, the newest first, by the name of the lane or of
# the sentence laid from the routes, each with the places of the current; one not here has had only
# its current wording.
EARLIER = {
    "follow_routes": follow_routes.WORDING_EARLIER,
    "result": follow_routes.RESULT_EARLIER,
}
# The lanes, and the sentence laid from the routes, that name the commands a subagent may run,
# each with the place they lie in; a subagent with lanes may run no other command.
RUNS = {**dict(run_only.COMMANDS), "result": "commands"}
# Where a wording shows what the lane takes, in quotes, by the name of its place.
TAKEN = re.compile(r"`<([a-z]+)>`")
# A thing given for each run: a name in braces, the braces wrapping the whole take.
GIVEN = re.compile(r"\{[^{}]+\}")


def action(lane: str) -> str:
    """The action the lane, or the sentence laid from the routes, watches."""
    return ROUTED[lane][0] if lane in ROUTED else LANES[lane].ACTION


def kind(lane: str) -> str:
    """The type of check that holds the lane: its own, or follow_routes for a sentence laid from the
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


def runs(lane: str, takes: list[str]) -> list[str]:
    """The commands the lane, taking the things, lets its subagent run: its takes in the place
    of its commands; none where it names no command."""
    return placed(lane, takes)[RUNS[lane]] if lane in RUNS else []


def ends(lane: str) -> bool:
    """Whether the lane is checked as the subagent gives its result: a lane of the end, or one of
    the trace kind, whose step must be done by then."""
    return lane in END or lane in TRACE


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
    return made(wording(lane), lane, takes)


def made(said: str, lane: str, takes: list[str]) -> str:
    """The wording given of the lane with the things in each place, as `sentence` makes it."""
    if not takes:
        return said
    found = placed(lane, takes)
    # Given as a function, the text put in is taken as it is, a backslash in it among the rest.
    return TAKEN.sub(lambda m: listed(found[m[1]]) if found[m[1]] else "", said)


def earlier(lane: str, takes: list[str]) -> list[str]:
    """The lane's sentence in each wording lane laid before the current one, the newest first, so
    a step laid before is told from one whose words are the user's own; none where lane
    has laid only the current one."""
    return [made(said, lane, takes) for said in EARLIER.get(lane, ())]


class Refused(NamedTuple):
    """Why a lane's takes cannot be laid, as the proposal's error goes on after `gives <lane> on
    <step>`, "" where they can; and whether the fix is to declare a dependency in the plugin's
    manifest."""

    said: str
    declare: bool = False


def refused(lane: str, takes: list[str], root: str) -> Refused:
    """Why the lane cannot be laid taking the things in the plugin at root, as `lay.py print`
    refuses it and the guard holds a lane laid to it: it takes nothing or an empty thing, its takes
    in its places are out of its IN, a take names a dependency's folder outside a command or a
    dependency the plugin's manifest does not declare, a take outside a command holds a value as a
    part, or in_form names a form it cannot read."""
    if not takes:
        return Refused("with no take")
    if not all(takes):
        return Refused("with a take that is empty")
    found = placed(lane, takes)
    out = schema.held(given_in(lane)["properties"]["takes"], found)
    if out is not None:
        return Refused(f"takes out of its places at {out.told()}")
    for place, each in found.items():
        command = (lane, place) in run_only.COMMANDS
        for named in (m for t in each for m in run_only.DEPENDENCY.finditer(t)):
            if not command:
                return Refused(f"`{named[0]}`, which only a command may name")
            if named["name"] not in run_only.dependencies(root):
                return Refused(
                    f"`{named[0]}`, which .claude-plugin/plugin.json does not declare among its"
                    " dependencies",
                    True,
                )
        for take in [] if command else each:
            for name in [] if GIVEN.fullmatch(take) else run_only.values_in(take):
                return Refused(f"`{{{name}}}` in a take, which only a command may hold as a part")
    for form in found.get("form", []) if lane == "in_form" else []:
        why = "" if GIVEN.fullmatch(form) else in_form.refused(form, root)
        if why:
            return Refused(f", which {why}")
    return Refused("")
