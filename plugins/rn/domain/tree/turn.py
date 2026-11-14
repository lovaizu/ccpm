"""Decides each deliverable whose turn has come to be doing: each one open that rests on no open
point and on no plan or deliverable not yet signed off, and which of those doing start side by side
beside the work that runs."""

from __future__ import annotations

from tree.design import DesignTree
from tree.sign_offs import SignOff


def due(tree: DesignTree, sign_offs: tuple[SignOff, ...]) -> tuple[str, ...]:
    """The path of each deliverable whose turn has come, in the order of the tree: open, with the
    plan signed off, no decision of its own open, and each deliverable it takes from or waits for
    done and signed off, with no decision of theirs open."""
    raise NotImplementedError("turn.due")


def marked(tree: DesignTree, sign_offs: tuple[SignOff, ...]) -> tuple[DesignTree, tuple[str, ...]]:
    """The tree with each deliverable whose turn has come marked doing, and the path of each one
    marked."""
    raise NotImplementedError("turn.marked")


def waiting_work(tree: DesignTree, running: tuple[str, ...]) -> tuple[str, ...]:
    """The path of each deliverable doing that no work that runs holds, given the path of each
    deliverable that a role running works on, in the order of the tree, so that those start side
    by side."""
    raise NotImplementedError("turn.waiting_work")
