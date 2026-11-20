"""S4: the commands a step runs, and the sentence of a step that runs another."""

from __future__ import annotations

import re

from place import Move
from rules import Rule, Step

from rule_types.words import listed


def judge_call(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges a call by the rule.

    Takes: the rule, the step it belongs to, and the move: a Bash call of the move's start.
    Gives: the step's sentence and the commands it runs, or that it runs none where the rule names
    none, where a command of the call, split at `|`, `&&`, `||`, `;`, and each newline, opens with
    the words of no command that the rule names and is no reporter of Lane's; None where each
    command of it opens with a named command's words, such as `git log` for `git log --oneline`,
    is a reporter, or is blank, such as a closing newline, which is no command.
    Changes: nothing.
    Refuses: nothing.
    """
    named = [command.split() for command in rule["commands"]]
    for part in re.split(r"\|\||&&|\||;|\n", move.event["tool_input"]["command"]):
        words = part.split()
        # A blank part, such as a closing newline, is no command, and a reporter is Lane's own.
        if not words or words[:1] in _REPORTERS:
            continue
        if any(words[: len(each)] == each for each in named):
            continue
        at = f"You're at the step `{step['name']}` of {move.role}, which runs"
        if not named:
            return f"{at} no command.\nRun it at a step that names it."
        return (
            f"{at} only {listed(rule['commands'])}.\n"
            "Run only those here, and the rest at a step that names them."
        )
    return None


# Lane's reporters, which each step runs, by the word that calls each.
_REPORTERS = [["lane-step"], ["lane-item"], ["lane-result"]]
