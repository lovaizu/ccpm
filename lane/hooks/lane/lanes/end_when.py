"""end_when: the subagent ends only once it has made an output its step names, such as the report it
is started to write. It is held as the subagent is about to end: an output it has not written in
this run, or written and then removed, is not made; one there from before is not either, as the
step's work is to make it, and a file left from an earlier run would let the subagent end with
nothing made."""

from __future__ import annotations

import os

import shell
from call import End, changed

ACTION = "end"
WORDING = "End only once `<output>` is made."
EVENTS = ("SubagentStop",)


def drifts(end: End, takes: list[str], root: str) -> bool:
    """Whether none of the outputs taken, each named from the folder the subagent ends in, where the
    guard stands, is there and was written by a call the subagent made, as the sentence lists them
    with `or`."""
    outputs = shell.paths(os.getcwd(), takes)
    made = end.made or []
    return bool(outputs) and not any(
        os.path.exists(o) and any(changed(c, o) for c in made) for o in outputs
    )
