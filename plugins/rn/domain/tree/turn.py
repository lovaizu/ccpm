"""Decides each deliverable whose turn has come to be doing: each one open that rests on no open
point and on no plan or deliverable not yet signed off. Which work of a role waits for a start
beside the starts that run is the adapter's, as Lane gives each start that runs only to it."""

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
