"""The parts of the work, which an item asked of each part is judged in."""

from __future__ import annotations

import os

import template

# A document's parts open at its top headings, of this level; any other file is one part.
DOCUMENT = ".md"
TOP = 2


def parts(work: list[str]) -> list[str]:
    """The parts of the work, each as its lines: a document's sections under its top headings,
    with the title and opening as one, and each other file whole; an empty file, or one not written
    yet, has none."""
    found: list[str] = []
    for path in work:
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        starts = [1] if lines else []
        if path.endswith(DOCUMENT):
            tops = [
                n
                for n, level, _ in template.headings(lines, template.body(lines))
                if level == TOP  # pragma: no mutate
            ]
            starts += [n for n in tops if n not in starts]
        ends = [n - 1 for n in starts[1:]] + [len(lines)]
        found += [f"{path}:{a}-{b}" for a, b in zip(starts, ends)]
    return found
