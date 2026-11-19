"""S6: a step's checklist, the items of the rule, each of which is done before the step, and the
sentence of a step done before each item."""

from __future__ import annotations

from place import Move
from rules import Rule, Step


def judge_mark(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges a mark by the rule.

    Takes: the rule, with its items, the step it belongs to, and the move: a reporter's mark of the
    step done, with the marks of items of the move's start that the run record holds.
    Gives: the step's sentence and each item of the rule not yet marked done; None where each is.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("rule_types.checklist.judge_mark")
