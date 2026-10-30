"""The session's learnings, kept in a file of their own in its folder: their form, those kept, and
the learnings listed by ID for the orchestrator to put to the user once the finished work is
approved."""

from __future__ import annotations

import os
import re

import repo
import steering
import stop

# The learnings' file, in the session's folder.
FILE = "learnings.md"
# Each learning, in the form of rn's learnings checklist's Format, which holds no heading.
LEARNING = re.compile(r"- (?P<id>L[0-9]+): (?P<said>\S.*)")
FORM = (
    "a learning as `- L<n>: <what happened, with the words it rests on, and where it would make"
    " later work better>`"
)


def path(folder: str) -> str:
    """The path of the session's learnings."""
    return os.path.join(folder, FILE)


def kept(folder: str) -> list[str]:
    """The lines of the session's learnings; none before any is made."""
    at = path(folder)
    return steering.trimmed(repo.read_text(at).splitlines()) if os.path.isfile(at) else []


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
    return steering.items_of(list(enumerate(lines, 1)), LEARNING, FORM)[1]


def listed(folder: str) -> dict[str, str]:
    """Every learning of the session, for the orchestrator to put to the user one per message once
    the finished work is approved, by ID, each as one line."""
    items = steering.items_of(list(enumerate(kept(folder))), LEARNING, FORM)[0]
    return {i.id: steering.said(i.lines).partition(": ")[2] for i in items}
