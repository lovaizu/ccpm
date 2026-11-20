"""How a rule type's sentence lists the values of its rule, such as the files a step writes."""

from __future__ import annotations


def listed(values: list[str], joined: str = "and") -> str:
    """The values as a sentence lists them.

    Takes: one value or more, such as `["CHANGELOG.md", "docs/changes/"]`, and the word that joins
    the last two, `and` unless given, or `or` for values offered as alternatives.
    Gives: them in their order, the last two joined by the word, such as
    `CHANGELOG.md and docs/changes/`, `a, b and c`, or `a, b or c`.
    Changes: nothing.
    Refuses: nothing.
    """
    *before, last = values
    return f"{', '.join(before)} {joined} {last}" if before else last
