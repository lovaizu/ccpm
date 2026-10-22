"""as_printed: the subagent hands on what a command its step names printed, word for word, such as
lane:up sending the builder the proposal `lay.py print` printed. A hand-on is an Agent call's prompt
or a SendMessage's message; the subagent's last reply is read on how it ends, not here. It is held
from the calls the subagent made before: once the command has run and printed, each hand-on is a
drift until one holds what it printed, a heading line beside it allowed."""

from __future__ import annotations

from call import HANDS, Call, handed

from lanes.start_with import runs

ACTION = "hand on"
WORDING = "Hand on `<input>` as it is."
TOOLS = tuple(HANDS)
# What the Bash tool gives back for a command that printed nothing.
SILENT = "(Bash completed with no output)"


def drifts(call: Call, takes: list[str]) -> bool:
    """Whether the call hands on while what a command taken last printed is due, and holds none of
    it: a command whose last run printed and did not fail, with no hand-on since holding it."""
    if call.action not in (ACTION,):
        return False
    due = [o for o in (due_output(call.before or [], t) for t in takes) if o]
    return bool(due) and not any(holds(handed(call), o) for o in due)


def due_output(before: list[Call], command: str) -> str:
    """What the command's last run among the calls before printed, where it is yet to be handed on;
    "" where it has not run, failed, printed nothing, or a hand-on since holds it."""
    due = ""
    for c in before:
        if runs(c, [command]):
            output = c.result.strip()
            due = "" if c.failed or output in (SILENT,) else output
        elif due and holds(handed(c), due):
            due = ""
    return due


def holds(text: str, output: str) -> bool:
    """Whether the text is the output word for word, alone or with one line of its own before it,
    such as a heading, or after it, blank lines and blanks around them left out."""
    text = text.strip()
    after_first = text.partition("\n")[2]
    before_last = text.rpartition("\n")[0]
    return output in (text, after_first.strip(), before_last.strip())
