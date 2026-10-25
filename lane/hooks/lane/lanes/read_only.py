"""read_only: the subagent reads only the inputs its step names, such as the file it is to answer,
and no file beside them, by the Read and Grep tools and by the commands that print what they
read; an input may be a folder, whose files it may read. Laid, the lane takes beside them the form
each in_form lane laid in the same subagent names."""

from __future__ import annotations

import os

import shell
import step
from call import READ_TOOLS, Call

ACTION = "read"
WORDING = "Read only `<input>`."
TOOLS = (*READ_TOOLS, "Bash")


def drifts(call: Call, takes: list[str], root: str) -> bool:
    """Whether the call reads a file or folder that is none of the inputs taken and in none of
    them, each input named from the folder the call is made in, where the guard stands."""
    inputs = [i for i in (shell.path(os.getcwd(), t) for t in takes) if i]
    return any(not any(shell.inside(p, i) for i in inputs) for p, _ in call.reads)


def beside(laid: list[tuple[str, list[str]]], root: str) -> list[str]:
    """The form each in_form lane laid in the subagent names, by the plugin's folder,
    which the lane lets the subagent read beside its inputs: its step tells it to write in the
    form, and the form, a file of the plugin, holds nothing of the project's work the lane keeps it
    to."""
    return [step.expanded(takes[1], root) for lane, takes in laid if lane == "in_form"]
