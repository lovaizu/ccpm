"""write_only: the subagent writes no file but the outputs its step names, such as `CHANGELOG.md`
alone, with the rest of the project left as it was."""

from __future__ import annotations

import os

import shell
from call import WRITERS, Call

ACTION = "write"
WORDING = "Write only `<output>`."
TOOLS = (*WRITERS, "Bash")


def drifts(call: Call, takes: list[str], root: str) -> bool:
    """Whether the call writes a file that is none of the outputs taken, each named from the folder
    the call is made in, where the guard stands; a command's write out of that folder is left out,
    as a command throws its output away in /dev/null or keeps it in a folder of its own to run what
    the work gives, as turn's generator does."""
    outputs = {os.path.realpath(t) for t in takes}
    here = os.getcwd()
    # Told by membership rather than `==`, as an order comparison such as `<=` would tell this
    # action from others too, and a mutant making it one would pass every test.
    counted = [f for f in call.written if call.action in (ACTION,) or shell.inside(f, here)]
    return any(f not in outputs for f in counted)
