"""S5: the steps of a role in their order, and the sentence of a step skipped or of an end before
each step is done."""

from __future__ import annotations

from place import Move
from rules import Rule, Step


def judge_mark(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges a mark by the rule.

    Takes: the rule, the step it belongs to, and the move: a reporter's mark of the step done, with
    the marks of the move's start that the run record holds.
    Gives: the step's sentence and the step due, where a step before it isn't marked done; None
    where each is.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("rule_types.order.judge_mark")


def judge_end(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges an end by the rule.

    Takes: the rule, the step it belongs to, and the move: the end of the move's start, with its
    marks that the run record holds, rule_types asking it only of the steps before the one at
    which a result that ends the start lets it end.
    Gives: the step's sentence, where the step isn't marked done; None where it is.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("rule_types.order.judge_end")
