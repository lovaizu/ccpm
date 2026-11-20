"""S7: the results a role gives, by which its run moves on, those that end its start at the step,
and the sentence of an end with no result of them."""

from __future__ import annotations

from place import Move
from rules import Rule, Step

from rule_types.words import listed


def given(move: Move) -> str | None:
    """The latest result that the move's start gave.

    Takes: a move of a subagent's start, its run as the record stands.
    Gives: the result of the latest `result` entry of the run with the move's `agent_id`; None
    where the run holds none.
    Changes: nothing.
    Refuses: nothing.
    """
    results = [
        entry["result"]
        for entry in move.run.entries
        if entry["kind"] == "result" and entry.get("agent_id") == move.agent_id
    ]
    return results[-1] if results else None


def judge_end(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges an end by the rule.

    Takes: the rule, the step it belongs to, and the move: the end of the move's start, with the
    result that its reporter gave, as the run record holds.
    Gives: the step's sentence and the results it may give, offered with the last two joined by
    `or`, where the start gave no result or one
    that neither the rule's `results` nor its `ends` name; for a rule that names only `ends`, the
    sentence tells the AI to mark the step done, and says that those results end the start only
    where it can't go on; None where it gave one of them.
    Changes: nothing.
    Refuses: nothing.
    """
    results, ends = rule.get("results", []), rule.get("ends", [])
    if given(move) in results + ends:
        return None
    if not results:
        return (
            f"You're at the step `{step['name']}` of {move.role}, whose work isn't done.\n"
            f"Do it and mark it done with lane-step {step['name']}; give"
            f" {listed(ends, 'or')} with lane-result only where you can't go on."
        )
    return (
        f"You end the step `{step['name']}` of {move.role} with no result it may give.\n"
        f"Give {listed(results + ends, 'or')} with lane-result first."
    )
