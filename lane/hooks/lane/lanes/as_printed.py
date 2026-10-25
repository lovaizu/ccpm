"""as_printed: the subagent hands on what a command its step names printed, word for word, as the
next thing it does, such as turn:up handing on the questions `turn.py questions` printed. A
hand-on is an Agent call's prompt, a SendMessage's message or the subagent's last reply, so the lane
is held both on a tool call and as the subagent is about to end. It is held from the calls the
subagent made before and the replies that ended its turn: once the command has run and printed,
each call, and the last reply, is a drift until a hand-on holds what it printed, a heading line
beside it allowed, as a call made first, such as one taking an answer that came meanwhile, acts
before the print has reached whoever it is for."""

from __future__ import annotations

from collections.abc import Sequence

import template
from call import Call, End, handed, runs
from record import SILENT

ACTION = "hand on"
WORDING = "Hand on `<command>` as it is."
# Any call may come before the hand-on, so every tool is watched, as a matcher's pattern.
TOOLS = (".*",)
EVENTS = ("PreToolUse", "SubagentStop")


def drifts(given: Call | End, takes: list[str], root: str) -> bool:
    """Whether the call is made, or the subagent ends with its last reply, while what a command
    taken last printed is due, and is no hand-on holding it: a command whose last run printed and
    did not fail, with no hand-on since holding it."""
    if isinstance(given, End):
        before, text = given.made, given.reply
    else:
        before, text = given.before, handed(given)
    due = [o for o in (due_output(before, t) for t in takes) if o]
    return bool(due) and not any(holds(text, o) for o in due)


def due_output(before: Sequence[Call], command: str) -> str:
    """What the command's last run among the calls before printed, where it is yet to be handed on;
    "" where it has not run, failed, printed nothing, or a hand-on since holds it."""
    due = ""
    for c in before:
        if runs(c, [command]):
            output = c.result.strip()
            due = "" if c.failed or output == SILENT else output
        elif due and holds(handed(c), due):
            due = ""
    return due


def holds(text: str, output: str) -> bool:
    """Whether the text is the output word for word, alone or with one line of its own before it,
    such as a heading, or after it, blank lines and blanks around them left out, and a Markdown
    code fence around it too, as a reply sets a print apart, where the output holds none."""
    if not any(map(template.FENCE.match, output.split("\n"))):
        text = "\n".join(line for line in text.split("\n") if not template.FENCE.match(line))
    text = text.strip()
    after_first = text.partition("\n")[2]
    before_last = text.rpartition("\n")[0]
    return output in (text, after_first.strip(), before_last.strip())
