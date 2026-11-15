"""Decides each deliverable's turn: it comes once the deliverable rests on no open point and on
nothing not signed off, and tree.py marks it doing."""

from __future__ import annotations

from tree.design import DesignTree
from tree.sign_offs import SignOffs


def mark_doing(tree: DesignTree, signed: SignOffs) -> tuple[DesignTree, tuple[str, ...]]:
    """The tree with each deliverable whose turn has come marked doing.

    Takes: the tree, and the run's sign-offs.
    Gives: the tree so marked, and the path of each deliverable it marked.
    Changes: nothing.
    Refuses: nothing.
    Carries: S2 `K->>T: writes it, and commits it with each deliverable whose turn has come marked
    doing`, and `T-->>K: ... each deliverable marked doing`; S3 the same after `/rn:ty`.
    """
    raise NotImplementedError("turn.mark_doing")


def doing(tree: DesignTree) -> tuple[str, ...]:
    """Each deliverable doing.

    Takes: the tree.
    Gives: the path of each deliverable marked doing, in the order of the work.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `A->>T: gets each deliverable doing`.
    """
    raise NotImplementedError("turn.doing")
