"""S1: the files a step writes, a folder letting through each file under it, and the sentence of a
step that writes another."""

from __future__ import annotations

import os

from place import Move
from rules import Rule, Step


def judge_call(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges a call by the rule.

    Takes: the rule, the step it belongs to, and the move: a Write or Edit of the move's start.
    Gives: the step's sentence and the files it writes, where the call writes a file that no path of
    the rule names and that lies under no folder it names; None where it does.
    Changes: nothing.
    Refuses: nothing.
    """
    cwd = os.path.realpath(move.event["cwd"])
    path = os.path.realpath(os.path.join(cwd, move.event["tool_input"]["file_path"]))
    written = os.path.relpath(path, cwd)
    paths = rule["paths"]
    if any(written == p or (p.endswith("/") and written.startswith(p)) for p in paths):
        return None
    named = ", ".join(paths[:-1]) + " and " + paths[-1] if len(paths) > 1 else paths[0]
    return (
        f"You're at the step `{step['name']}` of {move.role}, which writes only {named}.\n"
        f"Write there instead of {written}."
    )
