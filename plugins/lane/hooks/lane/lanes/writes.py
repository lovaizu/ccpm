"""S1: the files a step writes, a folder letting through each file under it, and the sentence of a
step that writes another."""

from __future__ import annotations

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
    raise NotImplementedError("lanes.writes.judge_call")
