"""The session's learnings, kept in a file of their own in its folder: their form, those kept, and
the learnings listed by ID for the orchestrator to put to the user once the finished work is
approved."""

from __future__ import annotations

import itertools
import os
import re
from typing import NamedTuple

import repo
import stop

# The learnings' file, in the session's folder.
FILE = "learnings.md"
# Each learning, in the form of rn's learnings checklist's Format, which holds no heading.
LEARNING = re.compile(r"- (?P<id>L[0-9]+): (?P<said>\S.*)")
FORM = (
    "a learning as `- L<n>: <what happened, with the words it rests on, and where it would make"
    " later work better>`"
)


def trimmed(lines: list[str]) -> list[str]:
    """The lines without the blank ones they open and end with."""
    words = [k for k, line in enumerate(lines) if line.strip()]
    return lines[words[0] : words[-1] + 1] if words else []


class Item(NamedTuple):
    """A learning: its ID, and its lines with their numbers, its first and each indented or blank
    under it."""

    id: str
    lines: list[tuple[int, str]]


def items_of(part: list[tuple[int, str]]) -> tuple[list[Item], str]:
    """Each learning of the part, a list whose items each open with `- ` in the form of a learning,
    and go on in lines indented under it; with the point the part is out of that form by, at its
    line, "" where it holds: a line neither, an item out of the form, or an ID again."""
    found: list[Item] = []
    for n, line in part:
        if line.startswith("- "):
            item = LEARNING.fullmatch(line)
            if item is None:
                return found, f"line {n}: expected {FORM}, found `{line}`"
            if item["id"] in [i.id for i in found]:
                return found, f"line {n}: expected each ID once, found {item['id']} again"
            found.append(Item(item["id"], [(n, line)]))
        elif found and (line.startswith("  ") or not line.strip()):
            found[-1].lines.append((n, line))
        else:
            # The lines are trimmed, so a blank line comes only under a learning.
            return (
                found,
                f"line {n}: expected {FORM}, or a line indented under one, found `{line}`",
            )
    return found, ""


def said(lines: list[tuple[int, str]]) -> str:
    """The first of the lines and those it runs on to, until a blank line, as one line, without the
    indent of each."""
    return " ".join(itertools.takewhile(bool, (line.strip() for _, line in lines)))


def path(folder: str) -> str:
    """The path of the session's learnings."""
    return os.path.join(folder, FILE)


def kept(folder: str) -> list[str]:
    """The lines of the session's learnings; none before any is made."""
    at = path(folder)
    return trimmed(repo.read_text(at).splitlines()) if os.path.isfile(at) else []


def write(folder: str, lines: list[str]) -> None:
    """Writes the session's learnings, once each is an item in the form of a learning, the lines
    indented under it its own; stops otherwise, writing nothing."""
    at = path(folder)
    point = out(lines)
    if point:
        raise stop.Stop(
            f"rn: {at} would be out of its form: {point}; nothing is kept: write the part it puts"
            " back again"
        )
    repo.write_text(at, "\n".join(lines) + "\n")


def out(lines: list[str]) -> str:
    """The point the session's learnings are out of their form by, each an item in the form of a
    learning, the lines indented under it its own, at its line, counted from 1; "" where they
    hold."""
    return items_of(list(enumerate(lines, 1)))[1]


def listed(folder: str) -> dict[str, str]:
    """Every learning of the session, for the orchestrator to put to the user one per message once
    the finished work is approved, by ID, each as one line."""
    items = items_of(list(enumerate(kept(folder))))[0]
    return {i.id: said(i.lines).partition(": ")[2] for i in items}
