"""Decides each deliverable's turn: it comes once the deliverable rests on no open point and on
nothing not signed off, and tree.py marks it doing."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

from tree.design import DesignTree, deliverables
from tree.sign_offs import Kind, SignOffs, State


def mark_doing(tree: DesignTree, signed: SignOffs) -> tuple[DesignTree, tuple[str, ...]]:
    """The tree with each deliverable whose turn has come marked doing.

    Takes: the tree, and the run's sign-offs.
    Gives: the tree so marked, and the path of each deliverable it marked, in the order of the
    work: each open deliverable once the plan's latest sign-off is signed off, no decision under it
    is open, and each deliverable of the tree that its inputs or preconditions name has its latest
    sign-off signed off; the tree as it was, and none, while the plan isn't signed off.
    Changes: nothing.
    Refuses: nothing.
    Carries: S2 `K->>T: writes it, and commits it with each deliverable whose turn has come marked
    doing`, and `T-->>K: ... each deliverable marked doing`; S3 the same after `/rn:ty`.
    """
    latest = _latest(signed)
    if latest.get((Kind.PLAN, "")) is not State.SIGNED_OFF:
        return tree, ()
    data = copy.deepcopy(dict(tree.data))
    each = deliverables(DesignTree(data))
    paths = {other["path"] for other in each}
    marked = []
    for deliverable in each:
        rests_on = set(deliverable.get("inputs", []) + deliverable.get("preconditions", [])) & paths
        signed_off = all(latest.get((Kind.DELIVERABLE, p)) is State.SIGNED_OFF for p in rests_on)
        if deliverable["status"] == "open" and signed_off and not _open_point(deliverable):
            deliverable["status"] = "doing"
            marked.append(deliverable["path"])
    return DesignTree(data), tuple(marked)


def doing(tree: DesignTree) -> tuple[str, ...]:
    """Each deliverable doing.

    Takes: the tree.
    Gives: the path of each deliverable marked doing, in the order of the work.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `A->>T: gets each deliverable doing`.
    """
    return tuple(d["path"] for d in deliverables(tree) if d.get("status") == "doing")


def _latest(signed: SignOffs) -> dict[tuple[Kind, str], State]:
    """Where the latest sign-off of each thing put up stands, by its kind and what it puts up."""
    return {(each.kind, each.what): each.state for each in signed.each}


def _open_point(node: Mapping[str, Any]) -> bool:
    """Whether a decision under the node is still open."""
    under = node.get("necessary_conditions", []) + node.get("decisions", [])
    return any(each.get("decided", "") is None or _open_point(each) for each in under)
