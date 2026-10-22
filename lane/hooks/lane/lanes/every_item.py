"""every_item: the subagent answers every item of an input its step names, such as each finding of a
review, before it ends. It is held as the subagent is about to end, on the items a check can tell
apart: an item is a top-level item of a Markdown list in the input, keyed by the ID it begins with,
such as `B-1`, `R33` or `KR1.1`; it is answered where its key stands in the subagent's last reply
or in a file it wrote in this run, the input left out, as rewriting the input keeps every key in it.
An item that begins with no ID is not counted, as no text tells an answer to it from any other."""

from __future__ import annotations

import os
import re

import shell
from call import End, changed

ACTION = "end"
WORDING = "Answer every item of `<input>`."
EVENTS = ("SubagentStop",)
# A top-level list item, its marker at the line's start, and the ID it begins with: capitals, a
# hyphen or not, a number, and numbers after a point, set in Markdown's bold, code or brackets or
# not, and followed by a colon, a point, a bracket, a blank or the line's end.
ITEM = re.compile(
    r"^(?:[-*+]|[0-9]+[.)])[ \t]+[*_`\[]*(?P<key>[A-Z][A-Za-z]*-?[0-9]+(?:\.[0-9]+)*)"
    r"[*_`\]]*(?=[:.)\s]|$)",
    re.MULTILINE,
)


def drifts(end: End, takes: list[str], root: str) -> bool:
    """Whether an item of an input taken, each named from the folder the subagent ends in, where
    the guard stands, has a key that stands in none of what answers it."""
    inputs = shell.paths(os.getcwd(), takes)
    written = {f for c in end.made or [] for f in c.written if changed(c, f)}
    answers = [end.reply, *(text(f) for f in sorted(written - set(inputs)))]
    return any(
        not any(stands(key, a) for a in answers) for i in inputs for key in ITEM.findall(text(i))
    )


def stands(key: str, answer: str) -> bool:
    """Whether the key stands in the answer as a word of its own, so `B-1` is not found in `B-12`,
    `B-1.2` or `AB-1`."""
    return (
        re.search(rf"(?<![A-Za-z0-9-]){re.escape(key)}(?![A-Za-z0-9]|[.-][0-9])", answer)
        is not None
    )


def text(file: str) -> str:
    """The file's text; none where it cannot be read."""
    try:
        with open(file, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""
