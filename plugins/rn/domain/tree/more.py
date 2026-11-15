"""Decides which `more` of an evaluator tree.py keeps for the next round: only one whose necessary
condition has a decision that changed since the round's cut, as a fix beside the design rests on no
decision."""

from __future__ import annotations

from dataclasses import dataclass

from tree.design import DesignTree


@dataclass(frozen=True)
class More:
    """An evaluator's `more` that the orchestrator judged the people fall short by: the deliverable
    by its path, the necessary condition by its ID, and its `good_when`."""

    deliverable: str
    condition: str
    good_when: str


def keepable(at_cut: DesignTree, now: DesignTree, more: More) -> None:
    """Whether a more may be kept.

    Takes: the tree as the round's cut took it, the tree with the tree-keeper's change, and the
    more.
    Gives: nothing, where a decision that answers the more's necessary condition differs between
    the two.
    Changes: nothing.
    Refuses: fault.Wrong, naming the more's necessary condition, where none does.
    Carries: S1 `alt no decision that answers the more's necessary condition changed since the
    round's cut`, and `T-->>K: refuses the more, naming its necessary condition`.
    """
    raise NotImplementedError("more.keepable")
