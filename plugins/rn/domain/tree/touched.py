"""Decides which nodes of the design tree a change touches, for the tree-keeper to check that each
agrees with it: the path up from each node changed, and each node that rests on it by path."""

from __future__ import annotations

from collections.abc import Sequence

from tree.design import DesignTree


def touched(tree: DesignTree, changed: Sequence[str]) -> tuple[str, ...]:
    """Each node that the nodes changed touch.

    Takes: the tree changed, and the path of each node changed.
    Gives: the path of each node touched, the path up included, each once, in the order of the tree.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `T-->>K: what changed, and each node they touch`; S2 and S3 `T-->>K: what changed,
    each node it touches`.
    """
    raise NotImplementedError("touched.touched")
