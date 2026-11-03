"""The files and the parts of the work, which an item asked of each part is judged in: the work
named by files or folders, the generator choosing each file inside a folder, its name and what it
holds (dev/turn/architecture.md, Components)."""

from __future__ import annotations

import os

import template

# A document's parts open at its top headings, of this level; any other file is one part.
DOCUMENT = ".md"
TOP = 2


def files(paths: list[str]) -> list[str]:
    """Each file at the paths: a folder's files at any depth, each named by the path from the
    folder as it is named, in the order of their paths; any other path itself, a file not written
    yet among them."""
    found: list[str] = []
    for path in paths:
        if os.path.isdir(path):
            found += sorted(os.path.join(top, n) for top, _, names in os.walk(path) for n in names)
        else:
            found.append(path)
    return found


def lines(path: str) -> list[str] | None:
    """The lines of the file at the path; None where it is not there or is not text, as such a
    file has no lines to give a Good at."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().splitlines()
    except (OSError, UnicodeDecodeError):
        return None


def parts(work: list[str]) -> list[str]:
    """The parts of the work, each as its lines: of each of its files, a document's sections under
    its top headings, with the title and opening as one, and each other file whole; an empty file,
    one not written yet, or one that is not text has none."""
    found: list[str] = []
    for path in files(work):
        held = lines(path)
        if held is None:
            continue
        starts = [1] if held else []
        if path.endswith(DOCUMENT):
            tops = [
                n
                for n, level, _ in template.headings(held, template.body(held))
                if level == TOP  # pragma: no mutate
            ]
            starts += [n for n in tops if n not in starts]
        ends = [n - 1 for n in starts[1:]] + [len(held)]
        found += [f"{path}:{a}-{b}" for a, b in zip(starts, ends)]
    return found
