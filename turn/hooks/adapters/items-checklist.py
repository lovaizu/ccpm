"""turn's adapter of lane's items port: given {"input": <path>, "text": <its text>} on stdin, prints
{"items": [<ID>, ...]}, the ID of each item of a turn checklist in the order it stands. An item is a
heading of the third level whose text begins `<ID>: `, its ID capitals, a hyphen and a number, such
as `B-1`, outside the frontmatter and any code fence, as turn's scripts/call.py reads a checklist;
lane's own reading takes list items instead. A Python 3 script on the standard library alone, as
lane runs it both beside the proposal and in the plugin, where turn's scripts are not beside it."""

from __future__ import annotations

import json
import re
import sys

# A heading of the third level, up to three blanks in, and its text after a blank, if any.
HEADING = re.compile(r" {0,3}###(?:[ \t]+(?P<text>.*))?")
# The marks that may close a heading's text, after a blank.
CLOSED = re.compile(r"(?:^|[ \t]+)#+[ \t]*$")
# The ID an item's heading text begins with, and the colon and blank after it.
ID = re.compile(r"(?P<id>[A-Z]+-\d+): ")
# What opens and closes frontmatter, on a line of its own at the top of the text.
MARK = "---"
# A line opening a code fence, up to three blanks in: three or more of one mark, a backtick or a
# tilde, and what follows them.
FENCE = re.compile(r" {0,3}(?P<marks>`{3,}|~{3,})(?P<rest>.*)")


def ids(text: str) -> list[str]:
    """The ID of each item heading of the text outside the frontmatter and any code fence, in
    order."""
    lines = text.splitlines()
    start = lines.index(MARK, 1) + 1 if lines[:1] == [MARK] and MARK in lines[1:] else 0
    found: list[str] = []
    # The marks of the fence open, None where none is.
    opened = None
    for line in lines[start:]:
        fence = FENCE.fullmatch(line)
        if opened is not None:
            opened = None if fence is not None and closes(fence, opened) else opened
            continue
        if fence is not None:
            opened = fence["marks"]
            continue
        heading = HEADING.fullmatch(line)
        item = heading and ID.match(CLOSED.sub("", heading["text"] or "").strip())
        if item:
            found.append(item["id"])
    return found


def closes(fence: re.Match[str], opened: str) -> bool:
    """Whether the fence line closes the fence opened by the marks: the same mark, at least as many,
    and blanks alone after."""
    marks = fence["marks"]
    return marks[0] == opened[0] and len(marks) >= len(opened) and not fence["rest"].strip()


if __name__ == "__main__":
    print(json.dumps({"items": ids(json.load(sys.stdin)["text"])}))
