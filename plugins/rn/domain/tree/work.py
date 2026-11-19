"""Decides the order that the work may take: each item of `work` names a node of the design tree,
and comes only once each deliverable that its node's inputs name is done."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # design.read runs this check, so the check takes only the type from it.
    from tree.design import Tree


def faults(tree: Tree) -> Sequence[str]:
    """Each fault of the work's order.

    Takes: the design tree.
    Gives: one line for each item that names no node, or comes before a deliverable that its node's
    inputs name and that isn't done; none where each holds.
    Refuses: nothing, as each fault is a line of what it gives."""
    nodes = {d["path"]: d for d in tree["deliverables"]}
    found: list[str] = []
    before: set[str] = set()
    for item in tree["work"]:
        node = nodes.get(item["path"])
        if node is None:
            found.append(f"work: {item['path']} names no deliverable of the design tree")
            continue
        found += [
            f"work: {item['path']} comes before {each}, which it takes and which isn't done"
            for each in node.get("inputs", [])
            if each in nodes and nodes[each]["status"] != "done" and each not in before
        ]
        before.add(item["path"])
    return found
