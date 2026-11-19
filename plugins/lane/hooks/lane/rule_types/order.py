"""S5: the steps of a role in their order, and the sentence of a step skipped or of an end before
each step is done."""

from __future__ import annotations

from place import Move, marked
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
    done = marked(move.run, move.agent_id)
    before = [each["name"] for each in move.steps[: move.steps.index(step)]]
    due = next((name for name in before if name not in done), None)
    if due is None:
        return None
    return (
        f"You're at the step `{due}` of {move.role}, which comes before `{step['name']}`.\n"
        f"Do `{due}` and mark it done with lane-step {due} first."
    )


def judge_end(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges an end by the rule.

    Takes: the rule, the step it belongs to, and the move: the end of the move's start, with its
    marks that the run record holds, rule_types asking it only of the steps before the one at
    which a result that ends the start lets it end.
    Gives: the step's sentence, where the step isn't marked done; None where it is.
    Changes: nothing.
    Refuses: nothing.
    """
    if step["name"] in marked(move.run, move.agent_id):
        return None
    return (
        f"You end before the step `{step['name']}` of {move.role} is done.\n"
        f"Do it and mark it done with lane-step {step['name']}."
    )
