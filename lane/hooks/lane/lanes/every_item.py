"""every_item: the subagent answers every item of an input its step names, such as each finding of a
review, before it ends. It is held as the subagent is about to end, on the items of the input as the
items port reads them, each its ID, such as `B-1`, `R33` or `KR1.1`; an item is answered where its
ID stands in the subagent's last reply or in a file it wrote in this run, the input left out, as
rewriting the input keeps every ID in it. An item with no ID is not counted, as no text tells an
answer to it from any other."""

from __future__ import annotations

import os
import re

import shell
from call import End, changed, file_text
from ports import Port

ACTION = "end"
WORDING = "Answer every item of `<input>`."
EVENTS = ("SubagentStop",)
# It reads the items of its input at the items port.
PORT = "items"


def drifts(end: End, takes: list[str], root: str, read: Port) -> bool:
    """Whether an item of an input taken, each named from the folder the subagent ends in, where
    the guard stands, read at the items port by read, has an ID that stands in none of what answers
    it."""
    inputs = shell.paths(os.getcwd(), takes)
    written = {f for c in end.made or [] for f in c.written if changed(c, f)}
    answers = [end.reply, *(file_text(f) or "" for f in sorted(written - set(inputs)))]
    return any(
        not any(stands(key, a) for a in answers)
        for i in inputs
        for key in read({"input": i, "text": file_text(i) or ""})["items"]
    )


def stands(key: str, answer: str) -> bool:
    """Whether the key stands in the answer as a word of its own, so `B-1` is not found in `B-12`,
    `B-1.2` or `AB-1`."""
    return (
        re.search(rf"(?<![A-Za-z0-9-]){re.escape(key)}(?![A-Za-z0-9]|[.-][0-9])", answer)
        is not None
    )
