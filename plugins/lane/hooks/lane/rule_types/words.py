"""How a rule type's sentence lists the values of its rule, such as the files a step writes."""

from __future__ import annotations


def listed(values: list[str]) -> str:
    """The values as a sentence lists them.

    Takes: one value or more, such as `["CHANGELOG.md", "docs/changes/"]`.
    Gives: them in their order, the last two joined by `and`, such as
    `CHANGELOG.md and docs/changes/`, or `a, b and c`.
    Changes: nothing.
    Refuses: nothing.
    """
    *before, last = values
    return f"{', '.join(before)} and {last}" if before else last
