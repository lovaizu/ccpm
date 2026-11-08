"""Decides which file holds a role's steps, its part, and how a part's numbered list reads as steps.

A role's part is the one Markdown file under the plugin's `domain/` that its entry names in
backticks, by the path the role reads it by, or else the entry itself.
"""

from __future__ import annotations

import os
import re
from typing import NamedTuple

import plugin

# A part that an entry names in backticks: a Markdown file under the plugin's domain/.
NAMED_PART = re.compile(r"`\$\{CLAUDE_PLUGIN_ROOT\}/(domain/[^`]+\.md)`")
# The first line of an item of a numbered list. It holds the item's number, then its text.
ITEM = re.compile(r"(\d+)\.\s+(.*)")
# A line that opens or closes a code fence.
FENCE = re.compile(r"(```|~~~)")


class Step(NamedTuple):
    """One item of a part's numbered list."""

    # The number that the item gives itself.
    number: int
    # The item's text, without its number, over each of its lines.
    says: str
    # The index of the item's first line in the part's text.
    first: int
    # The index of the item's last line.
    last: int


class Part(NamedTuple):
    """The file that holds a role's steps."""

    # The file's absolute path.
    path: str
    # The file's whole text.
    text: str
    # Whether the part is a file of its own, apart from the role's entry.
    own: bool
    # The items of the file's first numbered list, none where it has no such list.
    steps: list[Step]


def part(root: str, entry: plugin.Entry) -> Part:
    """The part of the role of the entry, in the plugin at the root.

    It raises `plugin.Fault` where the entry names one part, and the plugin doesn't hold it.
    """
    named = set(NAMED_PART.findall(entry.body))
    if len(named) != 1:
        with open(entry.path, encoding="utf-8") as f:
            text = f.read()
        return Part(entry.path, text, False, numbered(text))
    relative = named.pop()
    path = os.path.join(root, relative)
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        shown = os.path.relpath(entry.path, root)
        raise plugin.Fault(f"{shown} names its part {relative}, which isn't there") from None
    return Part(path, text, True, numbered(text))


def numbered(text: str) -> list[Step]:
    """The items of the first numbered list in the text, outside any code fence.

    An item runs on over each line indented under it, and over a blank line that an indented line
    follows. The list ends at the first other line that starts no item.
    """
    lines = text.split("\n")
    found: list[Step] = []
    fenced = False
    index = 0
    while index < len(lines):
        line = lines[index]
        if FENCE.match(line):
            fenced = not fenced
        item = None if fenced else ITEM.fullmatch(line)
        if item:
            last = _last_line(lines, index)
            says = "\n".join([item[2], *lines[index + 1 : last + 1]])
            found.append(Step(int(item[1]), says, index, last))
            index = last + 1
            continue
        if found and line.strip():
            break
        index += 1
    return found


def _last_line(lines: list[str], first: int) -> int:
    """The index of the last line of the item that starts at the line given."""
    last = first
    for index in range(first + 1, len(lines)):
        line = lines[index]
        if line[:1] in (" ", "\t") and line.strip():
            last = index
        elif line.strip():
            break
    return last
