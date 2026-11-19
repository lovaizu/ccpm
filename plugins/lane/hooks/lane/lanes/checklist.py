"""S6: a step's checklist, each item of which is done before the step, and the sentence of a step
done before each item."""

from __future__ import annotations

from place import Move
from rules import Rule, Step


def judge_mark(rule: Rule, step: Step, move: Move, items: list[str]) -> str | None:
    """Judges a mark by the rule.

    Takes: the rule, the step it belongs to, the move: a reporter's mark of the step done, with
    the marks of items of the move's start that the run record holds, and the step's items, as the
    plugin's checklist adapter gives them.
    Gives: the step's sentence and each item not yet marked done; None where each is.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("lanes.checklist.judge_mark")
