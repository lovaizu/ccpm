"""Decides which nodes of the design tree a change touches, as the design tree best practice lists
them after a change to a node: up to the goal, then the later decisions of the deliverable, then
the deliverables before and after it that it takes from or gives to. A node is named `goal`, a
deliverable's path, `<path> <condition>` for a necessary condition, and `<path> <condition>:
<about>` for a decision, with `-` for the condition of a `specific` deliverable's own decision."""

from __future__ import annotations

from tree.design import DesignTree

GOAL = "goal"


def changed(before: DesignTree | None, after: DesignTree) -> tuple[str, ...]:
    """Each node that differs between the tree before the change and after it, in the order of the
    tree after it; every node of `after` where there was no tree before."""
    raise NotImplementedError("touched.changed")


def touched(tree: DesignTree, nodes: tuple[str, ...]) -> tuple[str, ...]:
    """Each node of the tree that a change of the nodes touches, once, in the order the design tree
    best practice lists them, the nodes changed left out."""
    raise NotImplementedError("touched.touched")
