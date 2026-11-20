"""S2: the files a step never reads, and the sentence of a step that reads one or searches where
one lies."""

from __future__ import annotations

from named_files import named, of_call, reaches
from place import Move
from rules import Rule, Step

from rule_types.words import listed


def judge_call(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges a call by the rule.

    Takes: the rule, the step it belongs to, and the move: a Read or a Grep of the move's start,
    the calls that this rule judges alone, as a Glob reads no file's content and a Bash command that
    reaches such a file is held by the rule of commands of rule_types/commands.py.
    Gives: the step's sentence and the files it never reads, where a Read's `file_path` names one of
    the rule's paths or lies under one, asking to leave it unread, or where a Grep's search reaches
    one, as named_files.reaches says, asking for a path outside them instead of the one searched;
    None where it doesn't.
    Changes: nothing.
    Refuses: nothing.
    """
    read = of_call(move.event)
    if move.event["tool_name"] == "Grep":
        broken = reaches(rule["paths"], read)
        instead = f"Give Grep a path outside those files instead of {read}."
    else:
        broken = named(rule["paths"], read)
        instead = f"Leave {read} unread."
    if not broken:
        return None
    return (
        f"You're at the step `{step['name']}` of {move.role}, which never reads"
        f" {listed(rule['paths'])}.\n{instead}"
    )
