"""S4: the commands a step runs, and the sentence of a step that runs another."""

from __future__ import annotations

import re

from place import Move
from rules import Rule, Step

from rule_types.words import listed


def judge_call(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges a call by the rule.

    Takes: the rule, the step it belongs to, and the move: a Bash call of the move's start.
    Gives: the step's sentence and the commands it runs, where a command of the call, split at `|`,
    `&&`, `||`, and `;`, opens with the words of no command that the rule names and is no reporter
    of Lane's; None where each command of it opens with a named command's words, such as `git log`
    for `git log --oneline`, or is a reporter.
    Changes: nothing.
    Refuses: nothing.
    """
    named = [command.split() for command in rule["commands"]]
    for part in re.split(r"\|\||&&|\||;", move.event["tool_input"]["command"]):
        words = part.split()
        if words[:1] in _REPORTERS or any(words[: len(each)] == each for each in named):
            continue
        runs = f"only {listed(rule['commands'])}" if named else "no command"
        return (
            f"You're at the step `{step['name']}` of {move.role}, which runs {runs}.\n"
            f"Leave `{part.strip()}` to a step that names it."
        )
    return None


# Lane's reporters, which each step runs, by the word that calls each.
_REPORTERS = [["lane-step"], ["lane-item"], ["lane-result"]]
