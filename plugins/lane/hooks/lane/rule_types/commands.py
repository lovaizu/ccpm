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
    none, where a command of the call, split at `|`, `&&`, `||`, `;`, and each newline outside
    quotes, opens with the words of no command that the rule names and is no reporter of Lane's;
    None where each command of it opens with a named command's words, such as `git log` for
    `git log --oneline`, is a reporter, or is blank, such as a closing newline, which is no command.
    Changes: nothing.
    Refuses: nothing.
    """
    named = [command.split() for command in rule["commands"]]
    for part in _parts(move.event["tool_input"]["command"]):
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


def _parts(command: str) -> list[str]:
    """The commands of a Bash command, split at each operator outside quotes.

    Takes: the command of a Bash call.
    Gives: its parts, split at each match of _OPERATOR outside single and double quotes, where a
    backslash outside single quotes takes the character after it as a plain one, so that
    `git commit -m "Fix; test"` stays one part; where a quote doesn't close, its parts split at
    each match, quoted or not, as Bash runs each line before the one where the quote opened.
    Changes: nothing.
    Refuses: nothing.
    """
    found: list[str] = []
    begun = at = 0
    quote = ""
    while at < len(command):
        char = command[at]
        operator = None if quote else _OPERATOR.match(command, at)
        if char == "\\" and quote != "'":
            at += 2
        elif char in "'\"" and quote in ("", char):
            quote = "" if quote else char
            at += 1
        elif operator:
            found.append(command[begun:at])
            begun = at = operator.end()
        else:
            at += 1
    if quote:
        return _OPERATOR.split(command)
    return [*found, command[begun:]]


# The operators that end a command: `||` before `|`, so that `||` splits once.
_OPERATOR = re.compile(r"\|\||&&|\||;|\n")


# Lane's reporters, which each step runs, by the word that calls each.
_REPORTERS = [["lane-step"], ["lane-item"], ["lane-result"]]
