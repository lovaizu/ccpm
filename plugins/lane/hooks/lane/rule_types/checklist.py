"""S6: a step's checklist, the items of the rule or those that the plugin's command gives at the
mark, each of which is done before the step, and the sentence of a step done before each item."""

from __future__ import annotations

from typing import cast

import plugin_command
from place import Move
from plugin_command import Unchecked
from report import Report
from rules import Rule, Step

from rule_types.words import listed


def items(rule: Rule, move: Move) -> list[str]:
    """The items of the rule's checklist.

    Takes: the rule, with its `items` or its `command`, and the move: a reporter's mark of the step
    done, whose event's `cwd` is the conversation's folder.
    Gives: the rule's `items`, where it names them; else each line of the output of the rule's
    `command`, run in the event's `cwd` at the mark, as one item, none for an empty output.
    Changes: nothing of Lane's; the command may read the conversation's folder.
    Refuses: Unchecked, where the command exits other than 0, with the command, its code, and what
    it printed, or prints a line that is no one word, as lane-item takes an item as one word, with
    what it printed; or where it can't be run, with why.
    """
    if "items" in rule:
        return rule["items"]
    step = cast(Report, move.report)["step"]
    unchecked = f"Lane couldn't check the checklist of the step `{step}` of {move.role}"
    try:
        done = plugin_command.run(rule["command"], move.event["cwd"])
    except OSError as error:
        raise Unchecked(f"{unchecked}: it can't be run: {error}") from None
    if done.returncode:
        raise Unchecked(f"{unchecked}: {plugin_command.exited(rule['command'], done)}")
    lines = done.stdout.splitlines()
    if any(line.split() != [line] for line in lines):
        raise Unchecked(
            f"{unchecked}: {rule['command']} prints a line that isn't one word:\n"
            f"{(done.stdout + done.stderr).strip()}"
        )
    return lines


def judge_mark(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges a mark by the rule.

    Takes: the rule, with its items or the command that gives them, the step it belongs to, and the
    move: a reporter's mark of the step done, with the marks of items that Move.done gives
    for the move's start or turn.
    Gives: the step's sentence and each item that items gives not yet marked done; None where each
    item is marked done.
    Changes: nothing of Lane's; the rule's command may read the conversation's folder.
    Refuses: Unchecked, as items refuses.
    """
    done = move.done.items.get(step["name"], set())
    left = [item for item in items(rule, move) if item not in done]
    if not left:
        return None
    return (
        f"You're at the step `{step['name']}` of {move.role}, whose checklist isn't done:"
        f" {listed(left)}.\n"
        f"Do each and mark it done with lane-item {step['name']} <item> first."
    )
