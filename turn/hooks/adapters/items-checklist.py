"""turn's adapter of lane's items port: given {"input": <path>, "text": <its text>} on stdin, prints
{"items": [<ID>, ...]}, the ID of each item of a turn checklist in the order it stands. An item is a
heading of the third level whose text begins `<ID>: `, its ID capitals, a hyphen and a number, such
as `B-1`, outside the frontmatter and any code fence; lane's own reading takes list items instead.
This is turn's one reading of what an item is, which turn's scripts/call.py loads by its path too.
A Python 3 script on the standard library alone, as lane runs it both beside the proposal and in the
plugin, where turn's scripts are not beside it."""

from __future__ import annotations

import contextlib
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


def items(text: str) -> list[tuple[int, str]]:
    """Each item heading of the text outside the frontmatter and any code fence, in order, as the
    line it stands on, counted from 1, and its ID."""
    lines = text.splitlines()
    # Where the reading begins: the frontmatter's closing mark, a line that is no heading and no
    # fence, or the top where the text opens with no frontmatter closed.
    start = 0
    if lines[:1] == [MARK]:
        with contextlib.suppress(ValueError):
            start = lines.index(MARK, 1)
    found: list[tuple[int, str]] = []
    # The marks of the fence open, None where none is.
    opened = None
    for number, line in enumerate(lines[start:], start=start + 1):
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
            found.append((number, item["id"]))
    return found


def closes(fence: re.Match[str], opened: str) -> bool:
    """Whether the fence line closes the fence opened by the marks: its marks begin with those, so
    are the same mark, at least as many, and blanks alone come after."""
    return fence["marks"].startswith(opened) and not fence["rest"].strip()


if (
    __name__ == "__main__"  # pragma: no mutate
):
    print(json.dumps({"items": [i for _, i in items(json.load(sys.stdin)["text"])]}))
