"""Decides which `more` of an evaluator tree.py keeps for the next round: only one whose decision,
the one it names as the decision it changes, lies under its deliverable and changed since the
round's cut, as a fix beside the design rests on no decision, and only a decision under the
deliverable starts its next round."""

from __future__ import annotations

from dataclasses import dataclass

from tree.design import DesignTree


@dataclass(frozen=True)
class More:
    """An evaluator's `more` that the orchestrator judged the people fall short by: the deliverable
    by its path; the best practice by its kind, such as code or refactor-code, and the necessary
    condition by its ID, which together key it, as the kind's best practice and the refactor one
    share condition IDs such as N2; the decision it changes, by its path in the design tree, such as
    `deliverables/3/necessary_conditions/0/decisions/1`; and its `good_when`."""

    deliverable: str
    best_practice: str
    condition: str
    decision: str
    good_when: str


def keepable(at_cut: DesignTree, now: DesignTree, more: More) -> None:
    """Whether a more may be kept.

    Takes: the tree as the round's cut took it, the tree with the tree-keeper's change, and the
    more.
    Gives: nothing, where the decision at the more's path lies under the more's deliverable and
    differs between the two, including one that the cut didn't hold yet.
    Changes: nothing.
    Refuses: fault.Wrong, naming the more's best practice and necessary condition, where that
    decision isn't under the more's deliverable, as `cut.next_start` starts the deliverable's next
    round only once a decision under it changed, so an input's fault goes back to that input's
    deliverable; fault.Wrong, naming the more's best practice and necessary condition, where that
    decision is the same in both; fault.Wrong, naming the path, where the tree with the change holds
    no decision there, as a More kept changes one Decision; fault.Wrong, where the tree holds no
    deliverable at the more's path.
    Carries: S1 `alt the decision that the more names isn't under its deliverable, or didn't change
    since the round's cut`, and `T-->>K: refuses the more, naming its best practice and necessary
    condition`.
    """
    raise NotImplementedError("more.keepable")
