"""The lanes lane lays, one module each holding its action and its wording, as docs/lanes.md writes
them, and its check; and the sentence of each, made from its wording with what it takes, which the
step says and the guard tells, so the two never differ.

A lane's module gives `allows(value, takes, root, cwd)`: whether the call's value, the field of its
input the lane judges, goes through, given what the lane takes, the plugin's folder and the folder
the call is made in."""

from __future__ import annotations

import re

from lanes import run_only, write_only

LANES = {"write_only": write_only, "run_only": run_only}
# Where a wording shows what the lane takes, in quotes.
TAKEN = re.compile(r"`<[a-z]+>`")


def sentence(lane: str, takes: list[str]) -> str:
    """The lane's sentence: its wording with each thing it takes in quotes of its own, listed with
    commas and `or` before the last."""
    quoted = [f"`{t}`" for t in takes]
    listed = " or ".join(filter(None, [", ".join(quoted[:-1]), quoted[-1]]))
    # Given as a function, the text put in is taken as it is, a backslash in it among the rest.
    return TAKEN.sub(lambda _: listed, LANES[lane].WORDING)
