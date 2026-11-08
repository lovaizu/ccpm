"""Decides where a lane's sentence goes in a part's steps: at the end of its step, after every
word the user wrote, so that `lay.py` can put it in, take it out, and bring it to the current
wording without touching any other word."""

from __future__ import annotations

import step


def said(
    text: str, steps: list[step.Step], adds: dict[int, list[str]], drops: dict[int, list[str]]
) -> str:
    """The part's text with each sentence of `drops` taken out of its step, and each sentence of
    `adds` at the end of its step, in order, said once.

    steps holds the part's steps, as step.numbered reads them from the text. adds and drops each
    hold sentences by the number of the step they're about.
    """
    lines = text.split("\n")
    for item in reversed(steps):
        added = adds.get(item.number, [])
        dropped = drops.get(item.number, []) + added
        if not dropped:
            continue
        block = "\n".join(lines[item.first : item.last + 1])
        # The longest first, as an earlier wording may begin a later one, such as the result
        # sentence before Lane added its second sentence.
        for sentence in sorted(dropped, key=len, reverse=True):
            block = block.replace(" " + sentence, "")
        block = " ".join([block.rstrip(" "), *added]) if added else block
        lines[item.first : item.last + 1] = block.split("\n")
    return "\n".join(lines)


def reworded(text: str, steps: list[step.Step], pairs: list[tuple[str, str]]) -> str:
    """The part's text with each earlier sentence of the pairs put in its current wording, where a
    step says it, in its place."""
    lines = text.split("\n")
    for item in steps:
        block = "\n".join(lines[item.first : item.last + 1])
        for old, new in pairs:
            block = block.replace(old, new)
        lines[item.first : item.last + 1] = block.split("\n")
    return "\n".join(lines)
