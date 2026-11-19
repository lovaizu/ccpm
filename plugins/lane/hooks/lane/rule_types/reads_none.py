"""S2: the files a step never reads, and the sentence of a step that reads one."""

from __future__ import annotations

from named_files import named, of_call
from place import Move
from rules import Rule, Step

from rule_types.words import listed


def judge_call(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges a call by the rule.

    Takes: the rule, the step it belongs to, and the move: a Read, Grep, or Glob of the move's
    start, the calls that this rule judges alone, as a Bash command that reaches such a file is
    held by the rule of commands of rule_types/commands.py.
    Gives: the step's sentence and the files it never reads, where the call's `file_path` or `path`
    names one of the rule's paths or lies under one; None where it doesn't.
    Changes: nothing.
    Refuses: nothing.
    """
    read = of_call(move.event)
    if not named(rule["paths"], read):
        return None
    return (
        f"You're at the step `{step['name']}` of {move.role}, which never reads"
        f" {listed(rule['paths'])}.\n"
        f"Leave {read} unread."
    )
