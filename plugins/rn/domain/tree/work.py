"""Decides the design tree's work beyond its schema: an item follows its node when a change renames
it, and an item names a node of the tree and comes after each deliverable that its inputs name and
that isn't done, as the work then starts nothing on a guess."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any, cast

from fault import Wrong

from tree.design import DesignTree, deliverables


def renamed(before: DesignTree, after: DesignTree) -> DesignTree:
    """The tree changed, with each item of work following its node.

    Takes: the tree before a change, and the tree with it.
    Gives: the tree with the change, each item of its work that names the path that a deliverable
    held before the change, and that no deliverable holds after it, naming the path that the
    deliverable at the same place holds after it.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `K->>T: writes them with the work order, and commits them`, as tree.py rewrites an
    item whose node a change renames.
    """
    old = [each["path"] for each in deliverables(before)]
    new = [each["path"] for each in deliverables(after)]
    moved = {o: n for o, n in zip(old, new) if o != n and o not in new}
    data: Any = copy.deepcopy(dict(after.data))
    for item in data.get("work", []):
        if item["path"] in moved:
            item["path"] = moved[item["path"]]
    return DesignTree(data)


def hold(tree: DesignTree) -> None:
    """Whether the tree's work holds.

    Takes: the tree.
    Gives: nothing, where each item names a deliverable of the tree, and, for a point, a decision
    under it of that condition and about, and comes after an item that makes each deliverable that
    its deliverable's inputs name and that isn't done.
    Changes: nothing.
    Refuses: fault.Wrong, naming each item and why.
    Carries: S1 `alt an item of work names no node or comes before an input not done`, and
    `T-->>K: refuses the change, naming each`.
    """
    each = {d["path"]: d for d in deliverables(tree)}
    faults = []
    made: set[str] = set()
    for number, item in enumerate(cast(Any, tree.data).get("work", [])):
        at = f"work/{number}"
        node = each.get(item["path"])
        if node is None:
            faults.append(f"{at} names {item['path']}, no deliverable of the design tree")
            continue
        if item["do"] == "decide" and not _holds_point(node, item):
            faults.append(f"{at} names no point of {item['path']} by its condition and about")
        waits = [
            p
            for p in node.get("inputs", [])
            if p in each and each[p]["status"] != "done" and p not in made
        ]
        if waits:
            faults.append(f"{at} comes before {', '.join(waits)}, which its inputs name")
        if item["do"] == "make":
            made.add(item["path"])
    if faults:
        raise Wrong("the design tree's work doesn't hold: " + "; ".join(faults))


def _holds_point(node: Mapping[str, Any], item: Mapping[str, Any]) -> bool:
    """Whether the deliverable holds a decision of the item's condition and about."""
    if "necessary_conditions" in node:
        under = [c for c in node["necessary_conditions"] if c["id"] == item.get("condition")]
        decisions = [d for c in under for d in c["decisions"]]
    else:
        decisions = list(node.get("decisions", []))
    return any(d["about"] == item.get("about") for d in decisions)
