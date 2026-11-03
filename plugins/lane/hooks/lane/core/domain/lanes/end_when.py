"""end_when: the subagent gives its result only once an output its step names is made: there, as a
file or a folder, named from the folder it works in."""

from __future__ import annotations

import os

from done import Done

ACTION = "end"
WORDING = "End only once `<output>` is made."
CALLS = False


def missing(given: dict[str, list[str]], done: Done) -> str:
    """What is missing: that none of the outputs is there, as the sentence lists them with `or`;
    "" where one is."""
    outputs = given["output"]
    if any(os.path.exists(done.full(o)) for o in outputs):
        return ""
    return f"{' and '.join(f'`{o}`' for o in outputs)} not there"
