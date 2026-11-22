"""S8: the plugin's own check of a step, run in the conversation's folder, and the sentence of an
end that the check doesn't pass."""

from __future__ import annotations

import plugin_command
from place import Move
from plugin_command import Unchecked
from rules import Rule, Step


def judge_end(rule: Rule, step: Step, move: Move) -> str | None:
    """Judges an end by the rule.

    Takes: the rule, the step it belongs to, and the move: the end of the move's start, once its
    result and each step hold; rule_types asks it only of the steps before the one at which a
    result that ends the start lets it end, as that step itself isn't done.
    Gives: the step's sentence and what the check said, where the rule's command exits 1 in the
    event's `cwd`; None where it exits 0.
    Changes: nothing of Lane's; the check may read the conversation's folder.
    Refuses: Unchecked, where the command exits other than 0 or 1, as a check that couldn't check
    does, such as by 2, or by 127 for a command that the shell doesn't find, with the command, its
    code, and what it said; or where it can't be run, with why.
    """
    unchecked = f"Lane couldn't check the step `{step['name']}` of {move.role} by its check"
    try:
        done = plugin_command.run(rule["check"], move.event["cwd"])
    except OSError as error:
        raise Unchecked(f"{unchecked}: it can't be run: {error}") from None
    said = (done.stdout + done.stderr).strip()
    if not done.returncode:
        return None
    if done.returncode != 1:
        raise Unchecked(f"{unchecked}: {plugin_command.exited(rule['check'], done)}")
    return (
        f"You end the step `{step['name']}` of {move.role}, which its check doesn't pass:\n{said}"
    )
