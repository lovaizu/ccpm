"""read_only: the subagent reads only the inputs its step names, such as the file it is to answer,
and no file beside them, by the Read and Grep tools and by the commands that print what they
read; an input may be a folder, whose files it may read."""

from __future__ import annotations

import os

import shell
from call import READ_TOOLS, Call

ACTION = "read"
WORDING = "Read only `<input>`."
TOOLS = (*READ_TOOLS, "Bash")


def drifts(call: Call, takes: list[str], root: str) -> bool:
    """Whether the call reads a file or folder that is none of the inputs taken and in none of
    them, each input named from the folder the call is made in, where the guard stands."""
    inputs = [i for i in (shell.path(os.getcwd(), t) for t in takes) if i]
    return any(not any(shell.inside(p, i) for i in inputs) for p, _ in call.reads)
