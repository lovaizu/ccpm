"""Decides the order that the work may take: each item of `work` names a node of the design tree,
and comes only once each deliverable that its node's inputs name is done."""

from __future__ import annotations

from collections.abc import Sequence

from tree.design import Tree


def faults(tree: Tree) -> Sequence[str]:
    """Each fault of the work's order.

    Takes: the design tree.
    Gives: one line for each item that names no node, or comes before a deliverable that its node's
    inputs name and that isn't done; none where each holds.
    Refuses: nothing, as each fault is a line of what it gives."""
    raise NotImplementedError("work.faults")
