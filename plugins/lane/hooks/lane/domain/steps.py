"""A role's Step list: the numbered list under the `## Steps` heading of its file, and where a laid
sentence goes in it."""

from __future__ import annotations

import re

ITEM = re.compile(r"^(\d+)\. ")


class StepsError(ValueError):
    """The file holds no Step list, or not the step asked for."""


def _items(text: str) -> dict[int, tuple[int, int]]:
    """Each step's number, with the index of its first line and the index after its last."""
    lines = text.split("\n")
    if "## Steps" not in lines:
        raise StepsError("no `## Steps` heading")
    found: dict[int, tuple[int, int]] = {}
    current = 0
    for index in range(lines.index("## Steps") + 1, len(lines)):
        line = lines[index]
        if line.startswith("#"):
            break
        item = ITEM.match(line)
        if item:
            current = int(item.group(1))
            found[current] = (index, index + 1)
        elif current and line[:1].isspace() and line.strip():
            found[current] = (found[current][0], index + 1)
        elif line.strip():
            current = 0
    if not found:
        raise StepsError("no numbered step under `## Steps`")
    return found


def read(text: str) -> dict[int, str]:
    """Each step's text by its number, its lines joined by one blank. Raises StepsError where the
    file holds no Step list."""
    lines = text.split("\n")
    return {
        number: ITEM.sub("", " ".join(line.strip() for line in lines[first:after]), count=1)
        for number, (first, after) in _items(text).items()
    }


def laid(text: str, step: int, sentence: str, gone: list[str]) -> str:
    """The file's text with the sentence at the end of the step, each sentence of `gone` that
    ended it taken off first, and every other line as it was. Raises StepsError where the file
    lacks the step."""
    items = _items(text)
    if step not in items:
        raise StepsError(f"no step {step}")
    lines = text.split("\n")
    last = items[step][1] - 1
    line = lines[last].rstrip()
    ending = [f" {each}" for each in [*gone, sentence]]
    while any(line.endswith(each) for each in ending):
        line = next(line[: -len(each)] for each in ending if line.endswith(each))
    lines[last] = f"{line} {sentence}"
    return "\n".join(lines)
