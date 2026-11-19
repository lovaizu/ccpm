"""S6: a step's checklist, the items of the rule, each of which is done before the step, and the
sentence of a step done before each item."""

from __future__ import annotations

from place import Move
from rules import Rule, Step

from rule_types.words import listed


def judge_mark(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges a mark by the rule.

    Takes: the rule, with its items, the step it belongs to, and the move: a reporter's mark of the
    step done, with the marks of items of the move's start that the run record holds.
    Gives: the step's sentence and each item of the rule not yet marked done; None where each is.
    Changes: nothing.
    Refuses: nothing.
    """
    done = {
        entry.get("item")
        for entry in move.run.entries
        if entry["kind"] == "mark" and entry.get("agent_id") == move.agent_id
        if entry["step"] == step["name"]
    }
    left = [item for item in rule["items"] if item not in done]
    if not left:
        return None
    return (
        f"You're at the step `{step['name']}` of {move.role}, whose checklist isn't done:"
        f" {listed(left)}.\n"
        f"Do each and mark it done with lane-item {step['name']} <item> first."
    )
