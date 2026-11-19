"""Decides when a deliverable may say it's done: each `good` it holds is true, or, where it's
`specific`, its own `good` is."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # design.read runs this check, so the check takes only the type from it.
    from tree.design import Tree


def faults(tree: Tree) -> Sequence[str]:
    """Each deliverable that says it's done before it is.

    Takes: the design tree.
    Gives: one line for each deliverable whose status is done while a `good` it holds is false;
    none where each holds.
    Refuses: nothing, as each fault is a line of what it gives."""
    return [
        f"{d['path']} says it's done while a condition it holds isn't good"
        for d in tree["deliverables"]
        if d["status"] == "done" and not all(c["good"] for c in d.get("necessary_conditions", []))
    ]
