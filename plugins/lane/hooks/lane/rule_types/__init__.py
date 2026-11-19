"""Which rule types judge a call, a mark, and an end, and the order in which the guard asks them: a
mark for the step due, then the reads and the items its rules ask; an end for its result first,
then its steps, then the plugin's own check."""

from __future__ import annotations

from place import Move
from rules import Rules


def judge_call(rules: Rules, move: Move) -> str | None:
    """Judges a call of a start by each rule of its step that judges a call.

    Takes: the plugin's rules, and a `call` move, placed on its start's step.
    Gives: the sentence of the first rule the call breaks, by writes, reads_none, and commands;
    None where it breaks none, or where the move's step has no rule that judges a call.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("rule_types.judge_call")


def judge_mark(rules: Rules, move: Move, items: list[str]) -> str | None:
    """Judges a reporter's mark of a step done by each rule of the step that judges a mark.

    Takes: the plugin's rules, a `report` move of kind `step`, and the step's items, empty where
    no rule of the step asks for a checklist.
    Gives: the sentence of the first rule the mark breaks, by order, then reads_whole, then
    checklist; None where it breaks none.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("rule_types.judge_mark")


def judge_end(rules: Rules, move: Move) -> str | None:
    """Judges a start's end by each rule of its role that judges an end.

    Takes: the plugin's rules, and an `end` move.
    Gives: the sentence of the first rule the end breaks, by result, then order for each step,
    then check; None where it breaks none.
    Changes: nothing, though check runs the plugin's check.
    Refuses: OSError, where the plugin's check can't be run.
    """
    raise NotImplementedError("rule_types.judge_end")
