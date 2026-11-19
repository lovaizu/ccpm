"""S2: the files a step never reads, and the sentence of a step that reads one."""

from __future__ import annotations

from place import Move
from rules import Rule, Step


def judge_call(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges a call by the rule.

    Takes: the rule, the step it belongs to, and the move: a Read, Grep, or Glob of the move's
    start.
    Gives: the step's sentence and the files it never reads, where the call's `file_path` or `path`
    names one of the rule's paths or lies under one; None where it doesn't.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("lanes.reads_none.judge_call")
