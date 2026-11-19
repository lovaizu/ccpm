"""S1: the files a step writes, a folder letting through each file under it, and the sentence of a
step that writes another."""

from __future__ import annotations

from named_files import named, of_call
from place import Move
from rules import Rule, Step

from rule_types.words import listed


def judge_call(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges a call by the rule.

    Takes: the rule, the step it belongs to, and the move: a Write or Edit of the move's start.
    Gives: the step's sentence and the files it writes, where the call writes a file that no path of
    the rule names and that lies under no folder it names; None where it does.
    Changes: nothing.
    Refuses: nothing.
    """
    written = of_call(move.event)
    if named(rule["paths"], written):
        return None
    return (
        f"You're at the step `{step['name']}` of {move.role}, which writes only"
        f" {listed(rule['paths'])}.\n"
        f"Write there instead of {written}."
    )
