"""Decides how a task's reply lies on disk: one Markdown file for each task, each part after a
resume following the one before it, with a line between them saying when the limit stopped the
task and when it went on."""

from __future__ import annotations

from dataclasses import dataclass

from record.runs import Wait


@dataclass(frozen=True)
class Reply:
    """What one run of a task's session answered."""

    text: str


def part(reply: Reply, wait: Wait | None) -> str:
    """The text to add at the end of the task's reply file for the reply.

    Takes: the reply, and the wait that came before it, or None where it's the task's first part.
    Gives: the reply's text, after the line that says when the limit stopped the task and when it
    went on, where a wait came before it.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("record.replies.part")
