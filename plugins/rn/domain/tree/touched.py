"""Decides which nodes of the design tree a change touches, for the tree-keeper to check that each
agrees with it: the path up from each node changed, and each node that rests on it by path."""

from __future__ import annotations

from collections.abc import Sequence

from tree.design import DesignTree, deliverables, nodes


def touched(tree: DesignTree, changed: Sequence[str]) -> tuple[str, ...]:
    """Each node that the nodes changed touch.

    Takes: the tree changed, and the path of each node changed.
    Gives: the path of each node touched, the path up included, each once, in the order of the tree.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `T-->>K: what changed, and each node they touch`; S2 and S3 `T-->>K: what changed,
    each node it touches`.
    """
    found: set[str] = set()
    for path in changed:
        parts = path.split("/")
        found.update("/".join(parts[:end]) for end in range(2, len(parts), 2))
        found.update(_resting_on(tree, "/".join(parts[:2])))
    order = nodes(tree)
    return tuple(sorted(found, key=lambda path: order.index(path) if path in order else len(order)))


def _resting_on(tree: DesignTree, deliverable: str) -> list[str]:
    """The path of each deliverable whose inputs or preconditions name the path of the deliverable
    at the node's path, as it rests on it."""
    each = deliverables(tree)
    parts = deliverable.split("/")
    if len(parts) != 2 or parts[0] != "deliverables" or int(parts[1]) >= len(each):
        return []
    named = each[int(parts[1])]["path"]
    return [
        f"deliverables/{number}"
        for number, other in enumerate(each)
        if named in other.get("inputs", []) + other.get("preconditions", [])
    ]
