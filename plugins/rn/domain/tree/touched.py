"""Decides which nodes of the design tree a change touches: the nodes that differ from the tree as
last committed, and those that the links between the nodes reach from each, as the design tree
best practice's N4 lists them."""

from __future__ import annotations

from tree.form import Tree


def touched(tree: Tree, pointer: str) -> list[str]:
    """The nodes that a change to the node touches, to read again beside the change.

    Takes: the tree, and the changed node's JSON Pointer.
    Gives: the JSON Pointer of each node up to the goal; of each later decision of the same
    deliverable; of each deliverable that names the changed one's path in its inputs, or that it
    names there; and of each item of `work` that names its path; each once, from the goal down, the
    changed node left out.
    Changes: nothing.
    Refuses: Wrong where the pointer names no node, as `tree.form.at` refuses.
    """
    raise NotImplementedError("tree.touched.touched")


def changed(before: Tree, after: Tree) -> list[str]:
    """The nodes that a change made.

    Takes: the tree as last committed, and the tree as it stands.
    Gives: the JSON Pointer of each deepest node whose value differs, or that one of them holds
    and the other doesn't, from the goal down; none where they're equal.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("tree.touched.changed")
