"""The lanes lane lays, one module each holding its action and its wording, as docs/lanes.md writes
them, and its check; the sentences lane lays from the routes, follow_routes' on the orchestrator's
step and the result command on a subagent's last step, as docs/routes.md writes them; and the
sentence of each, made from its wording with what it takes, which the step says and the guard
tells, so the two never differ.

A lane's module gives `allows(value, takes, root, cwd)`: whether the call's value, the field of its
input the lane judges, goes through, given what the lane takes, the plugin's folder and the folder
the call is made in."""

from __future__ import annotations

import re

from lanes import follow_routes, run_only, write_only

LANES = {"write_only": write_only, "run_only": run_only}
# The sentences laid from the routes, each by the name a step's lanes give it, with its action and
# wording; follow_routes lays and checks both.
ROUTED = {
    "follow_routes": (follow_routes.ACTION, follow_routes.WORDING),
    "result": ("end", follow_routes.RESULT),
}
# Where a wording shows what the lane takes, in quotes.
TAKEN = re.compile(r"`<[a-z]+>`")


def action(lane: str) -> str:
    """The action the lane, or the sentence laid from the routes, watches."""
    return ROUTED[lane][0] if lane in ROUTED else LANES[lane].ACTION


def hook(lane: str) -> str:
    """The hook that checks the lane: its own, or follow_routes for a sentence laid from the
    routes."""
    return "follow_routes" if lane in ROUTED else lane


def sentence(lane: str, takes: list[str]) -> str:
    """The lane's sentence: its wording with each thing it takes in quotes of its own, listed with
    commas and `or` before the last; its wording alone where it takes nothing."""
    wording = ROUTED[lane][1] if lane in ROUTED else LANES[lane].WORDING
    if not takes:
        return wording
    quoted = [f"`{t}`" for t in takes]
    listed = " or ".join(filter(None, [", ".join(quoted[:-1]), quoted[-1]]))
    # Given as a function, the text put in is taken as it is, a backslash in it among the rest.
    return TAKEN.sub(lambda _: listed, wording)
