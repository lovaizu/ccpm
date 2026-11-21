"""S3: the files a step reads whole before it's done, and the sentence of a step done without
reading one whole."""

from __future__ import annotations

import os

from place import Move
from rules import Rule, Step

from rule_types.words import listed


def judge_mark(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges a mark by the rule.

    Takes: the rule, the step it belongs to, and the move: a reporter's mark of the step done, with
    the lines that Move.done gives read for the move's start or turn.
    Gives: the step's sentence and the lines of each file of the rule that no Read of the start or
    the turn has read; None where each file is read whole.
    Changes: nothing.
    Refuses: nothing.
    """
    unread = [
        f"{path} from its line {first}"
        for path in rule["paths"]
        for first in [_first_unread(move, path)]
        if first is not None
    ]
    if not unread:
        return None
    return (
        f"You're at the step `{step['name']}` of {move.role}, which reads whole"
        f" {listed(rule['paths'])}.\n"
        f"Read {listed(unread)} before you mark it done."
    )


def _first_unread(move: Move, path: str) -> int | None:
    """The first line of the file that no Read of the move's start or turn read, None where each
    is; a file counting the empty line after its last newline, as Read counts it."""
    with open(os.path.join(move.event["cwd"], path), encoding="utf-8") as f:
        lines = f.read().split("\n")
    read = move.done.lines.get(path, set())
    return next((line for line, _ in enumerate(lines, 1) if line not in read), None)
