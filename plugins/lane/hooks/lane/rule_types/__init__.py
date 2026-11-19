"""Which rule types judge a call, a mark, and an end, and the order in which the guard asks them: a
mark for the step due, then the reads and the items its rules ask; an end for its result first,
then each step up to the one whose result rule names the start's result among those that end it,
then the plugin's own check."""

from __future__ import annotations

from place import Move

from rule_types import checklist, commands, order, reads_none, reads_whole, writes

# The rule types that judge a call of each tool, by their names in a rule's `type`, in the order
# the guard asks them.
_CALLS = {
    "Write": {"writes": writes.judge_call},
    "Edit": {"writes": writes.judge_call},
    "Read": {"reads_none": reads_none.judge_call},
    "Bash": {"commands": commands.judge_call},
}


def judge_call(move: Move) -> str | None:
    """Judges a call of a start by each rule of its step that judges a call.

    Takes: a `call` move, placed on its start's step, with the steps that hold its start.
    Gives: the sentence of the first rule the call breaks, by writes, reads_none, and commands;
    None where it breaks none, or where the move's step has no rule that judges a call.
    Changes: nothing.
    Refuses: nothing.
    """
    tool = move.event.get("tool_name", "")
    if tool in ("Grep", "Glob"):
        raise NotImplementedError(f"rule_types.judge_call of {tool}")
    judges = _CALLS.get(tool, {})
    said = (
        judges[rule["type"]](rule, step, move)
        for step in move.steps
        if step["name"] == move.step
        for rule in step["rules"]
        if rule["type"] in judges
    )
    return next((each for each in said if each is not None), None)


def judge_mark(move: Move) -> str | None:
    """Judges a reporter's mark of a step done by each rule of the step that judges a mark.

    Takes: a `report` move of kind `step`, with the steps that hold its start.
    Gives: the sentence of the first rule the mark breaks, by order, then reads_whole, then
    checklist; None where it breaks none.
    Changes: nothing.
    Refuses: nothing.
    """
    marked = move.report["step"] if move.report else None
    said = (
        judge(rule, step, move)
        for kind, judge in _MARKS.items()
        for step in move.steps
        if step["name"] == marked
        for rule in step["rules"]
        if rule["type"] == kind
    )
    return next((each for each in said if each is not None), None)


def judge_end(move: Move) -> str | None:
    """Judges a start's end, or the main conversation's turn's end, by each rule of its role that
    judges an end.

    Takes: an `end` move of a subagent, or a `turn_end` move of the main conversation, with the
    steps that hold its start.
    Gives: the sentence of the first rule the end breaks, by the result rule of the step at which
    the start ends, the step due or else the last, then order for each step before the first whose
    result rule names the start's result among those that end it, or for each step where none
    does, then check; None where it breaks none.
    Changes: nothing, though check runs the plugin's check.
    Refuses: OSError, where the plugin's check can't be run.
    """
    raise NotImplementedError("rule_types.judge_end")


# The rule types that judge a mark, by their names in a rule's `type`, in the order the guard asks
# them.
_MARKS = {
    "order": order.judge_mark,
    "reads_whole": reads_whole.judge_mark,
    "checklist": checklist.judge_mark,
}
