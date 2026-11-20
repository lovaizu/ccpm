"""S6: a step's checklist, the items of the rule or those that the plugin's command gives at the
mark, each of which is done before the step, and the sentence of a step done before each item."""

from __future__ import annotations

import subprocess
from typing import cast

from place import Move, own_entries
from report import Report
from rules import Rule, Step

from rule_types.words import listed


class ItemsFailed(Exception):
    """The plugin's command of a checklist that exits other than 0, or prints a line that is no one
    word, said as the step's sentence with the command's output, so that the mark stops with it."""


def items(rule: Rule, move: Move) -> list[str]:
    """The items of the rule's checklist.

    Takes: the rule, with its `items` or its `command`, and the move: a reporter's mark of the step
    done, whose event's `cwd` is the conversation's folder.
    Gives: the rule's `items`, where it names them; else each line of the output of the rule's
    `command`, run in the event's `cwd` at the mark, as one item, none for an empty output.
    Changes: nothing of Lane's; the command may read the conversation's folder.
    Refuses: ItemsFailed, where the command exits other than 0, with what it printed, or prints a
    line that is no one word, as lane-item takes an item as one word; OSError, where the command
    can't be run.
    """
    if "items" in rule:
        return rule["items"]
    done = subprocess.run(
        rule["command"],
        shell=True,
        cwd=move.event["cwd"],
        capture_output=True,
        text=True,
        check=False,
    )
    lines = done.stdout.splitlines()
    if done.returncode or any(line.split() != [line] for line in lines):
        step = cast(Report, move.report)["step"]
        raise ItemsFailed(
            f"You're at the step `{step}` of {move.role}, whose checklist command fails:\n"
            f"{(done.stdout + done.stderr).strip()}\n"
            f"Mend {rule['command']}, which gives the items one word a line."
        )
    return lines


def judge_mark(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges a mark by the rule.

    Takes: the rule, with its items or the command that gives them, the step it belongs to, and the
    move: a reporter's mark of the step done, with the marks of items that place.own_entries gives
    for the move's start or turn.
    Gives: the step's sentence and each item that items gives not yet marked done; the sentence of
    ItemsFailed, where the command fails; None where each item is marked done.
    Changes: nothing of Lane's; the rule's command may read the conversation's folder.
    Refuses: OSError, where the rule's command can't be run.
    """
    try:
        listed_items = items(rule, move)
    except ItemsFailed as failed:
        return str(failed)
    done = {
        entry.get("item")
        for entry in own_entries(move.run, move.agent_id)
        if entry["kind"] == "mark" and entry["step"] == step["name"]
    }
    left = [item for item in listed_items if item not in done]
    if not left:
        return None
    return (
        f"You're at the step `{step['name']}` of {move.role}, whose checklist isn't done:"
        f" {listed(left)}.\n"
        f"Do each and mark it done with lane-item {step['name']} <item> first."
    )
