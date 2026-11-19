"""S3: the files a step reads whole before it's done, and the sentence of a step done without
reading one whole."""

from __future__ import annotations

from place import Move
from rules import Rule, Step


def judge_mark(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges a mark by the rule.

    Takes: the rule, the step it belongs to, and the move: a reporter's mark of the step done, with
    the reads of the move's start that the run record holds.
    Gives: the step's sentence and the lines of each file of the rule that no Read of the start has
    read; None where each file is read whole.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("lanes.reads_whole.judge_mark")
