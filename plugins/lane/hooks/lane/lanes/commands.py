"""S4: the commands a step runs, and the sentence of a step that runs another."""

from __future__ import annotations

from place import Move
from rules import Rule, Step


def judge_call(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges a call by the rule.

    Takes: the rule, the step it belongs to, and the move: a Bash call of the move's start.
    Gives: the step's sentence and the commands it runs, where the call runs a command that the rule
    doesn't name and that is no reporter of Lane's; None where it does.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("lanes.commands.judge_call")
