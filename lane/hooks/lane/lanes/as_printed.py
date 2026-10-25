"""as_printed: the subagent hands on what a command its step names printed, word for word, such as
lane:up giving the building AI the proposal `lay.py print` printed. A hand-on is an Agent call's
prompt, a SendMessage's message or the subagent's last reply, so the lane is held both on a tool
call and as the subagent is about to end. It is held from the calls the subagent made before and
the replies that ended its turn: once the command has run and printed, each hand-on is a drift
until one holds what it printed, a heading line beside it allowed."""

from __future__ import annotations

import template
from call import HANDS, Call, End, handed, runs

ACTION = "hand on"
WORDING = "Hand on `<command>` as it is."
TOOLS = tuple(HANDS)
EVENTS = ("PreToolUse", "SubagentStop")
# What the Bash tool gives back for a command that printed nothing.
SILENT = "(Bash completed with no output)"


def drifts(given: Call | End, takes: list[str], root: str) -> bool:
    """Whether the call hands on, or the subagent ends with its last reply, while what a command
    taken last printed is due, and holds none of it: a command whose last run printed and did not
    fail, with no hand-on since holding it."""
    if isinstance(given, End):
        before, text = given.made or [], given.reply
    elif given.action == ACTION:
        before, text = given.before or [], handed(given)
    else:
        return False
    due = [o for o in (due_output(before, t) for t in takes) if o]
    return bool(due) and not any(holds(text, o) for o in due)


def due_output(before: list[Call], command: str) -> str:
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
