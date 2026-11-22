"""Which rule types judge a call, a mark, and an end, and the order in which the guard asks them: a
mark for the step due, then the reads and the items its rules ask; an end for its result first,
then each step up to the one whose result rule names the start's result among those that end it,
then the plugin's own check of each of those steps, the step at which the start ends not done."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Callable

from place import Move
from plugin_command import Unchecked
from rules import Rule, Step

from rule_types import check, checklist, commands, order, reads_none, reads_whole, result, writes

# A rule type's judge of a call, a mark, or an end: the sentence of the rule broken, None for none.
Judge = Callable[[Rule, Step, Move], "str | None"]

# The rule types that judge a call of each tool, by their names in a rule's `type`, in the order
# the guard asks them.
_CALLS = {
    "Write": {"writes": writes.judge_call},
    "Edit": {"writes": writes.judge_call},
    "NotebookEdit": {"writes": writes.judge_call},
    "Read": {"reads_none": reads_none.judge_call},
    "Grep": {"reads_none": reads_none.judge_call},
    "Bash": {"commands": commands.judge_call},
}


def judge_call(move: Move) -> str | None:
    """Judges a call of a start by each rule of its step that judges a call.

    Takes: a `call` move, placed on its start's step, with the steps that hold its start.
    Gives: the sentence of the first rule the call breaks, by writes for a Write, an Edit, or a
    NotebookEdit, reads_none for a Read or a Grep, and commands for a Bash call; None where it
    breaks none, where the move's step has no rule that judges a call, or for a call of any other
    tool, such as a Glob, which reads no file's content.
    Changes: nothing.
    Refuses: nothing.
    """
    judges = _CALLS.get(move.event.get("tool_name", ""), {})
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
    Refuses: Unchecked, where it breaks none and a checklist couldn't be checked, as
    checklist.items refuses.
    """
    step_marked = move.report["step"] if move.report else None
    judged = (
        (judge, rule, step)
        for kind, judge in _MARKS.items()
        for step in move.steps
        if step["name"] == step_marked
        for rule in step["rules"]
        if rule["type"] == kind
    )
    return _first_broken(judged, move)


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
    Refuses: Unchecked, where it breaks none and a check couldn't check, as check.judge_end
    refuses, with what each such check said, one a line.
    """
    steps = move.steps
    done = move.done.steps
    # The step whose result rule judges the end: the first the start hasn't marked done, where its
    # rules give one, else its last; none where its result ends the start at a step, as a result
    # that a rule names among those that end the start is one it may give.
    gave = move.done.result
    ends_at = next((i for i, step in enumerate(steps) if gave in _ends(step)), None)
    due = [step for step in steps if step["name"] not in done][:1]
    ruled = [step for step in due if any(rule["type"] == "result" for rule in step["rules"])]
    ending = (ruled or steps[-1:]) if ends_at is None else []
    judged = (
        (judge, rule, step)
        for kind, judge, held in (
            ("result", result.judge_end, ending),
            ("order", order.judge_end, steps[:ends_at]),
            ("check", check.judge_end, steps[:ends_at]),
        )
        for step in held
        for rule in step["rules"]
        if rule["type"] == kind
    )
    return _first_broken(judged, move)


def _first_broken(judged: Iterable[tuple[Judge, Rule, Step]], move: Move) -> str | None:
    """The sentence of the first rule that the move breaks, each judged in turn and those after it
    left unjudged; where none breaks and a rule couldn't be checked, Unchecked with what each such
    rule said, one a line."""
    unchecked = []
    for judge, rule, step in judged:
        try:
            said = judge(rule, step, move)
        except Unchecked as couldnt:
            unchecked.append(str(couldnt))
            continue
        if said is not None:
            return said
    if unchecked:
        raise Unchecked("\n".join(unchecked))
    return None


def ended_at_a_step(move: Move) -> bool:
    """Whether a start, or the main conversation's turn, ends on a result that ends it at a step.

    Takes: an `end` move of a subagent, or a `turn_end` move of the main conversation, with the
    steps that hold its start.
    Gives: True where the result that Move.done gives is one that a step's result rule names
    among those that end the start there; False where it gave none, or another.
    Changes: nothing.
    Refuses: nothing.
    """
    gave = move.done.result
    return any(gave in _ends(step) for step in move.steps)


def _ends(step: Step) -> list[str]:
    """The results that the step's rules name as ending the start there, which only a result rule
    names."""
    return [end for rule in step["rules"] for end in rule.get("ends", [])]


# The rule types that judge a mark, by their names in a rule's `type`, in the order the guard asks
# them.
_MARKS = {
    "order": order.judge_mark,
    "reads_whole": reads_whole.judge_mark,
    "checklist": checklist.judge_mark,
}
