"""S8: the plugin's own check of a step, run in the conversation's folder, and the sentence of an
end that the check doesn't pass."""

from __future__ import annotations

from place import Move
from rules import Rule, Step


def judge_end(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges an end by the rule.

    Takes: the rule, the step it belongs to, and the move: the end of the move's start, once its
    result and each step hold.
    Gives: the step's sentence and what the check said, where the rule's command exits other than 0
    in the event's `cwd`; None where it passes.
    Changes: nothing of Lane's; the check may read the conversation's folder.
    Refuses: OSError, where the check can't be run.
    """
    raise NotImplementedError("lanes.check.judge_end")
