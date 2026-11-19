"""S7: the results a role gives, by which its run moves on, those that end its start at the step,
and the sentence of an end with no result of them."""

from __future__ import annotations

from place import Move
from rules import Rule, Step


def judge_end(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges an end by the rule.

    Takes: the rule, the step it belongs to, and the move: the end of the move's start, with the
    result that its reporter gave, as the run record holds.
    Gives: the step's sentence and the results it may give, where the start gave no result or one
    that neither the rule's `results` nor its `ends` name; None where it gave one of them.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("rule_types.result.judge_end")
