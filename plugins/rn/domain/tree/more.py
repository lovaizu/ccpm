"""Decides which `more` of an evaluator tree.py keeps for the next round: only one whose decision,
the one it names as the decision it changes, lies under its deliverable and changed since the
round's cut, as a fix beside the design rests on no decision, and only a decision under the
deliverable starts its next round."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from fault import Wrong

from tree.design import DesignTree, deliverables

# The path of a decision in the design tree.
_DECISION = re.compile(r"^deliverables/\d+/necessary_conditions/\d+/decisions/\d+$")


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
    tree_path = _tree_path(now, more.deliverable)
    if tree_path is None:
        raise Wrong(
            f"the more's deliverable {more.deliverable} is no deliverable of the design tree"
        )
    named = f"the more of {more.condition} of the {more.best_practice} best practice"
    if not more.decision.startswith(tree_path + "/"):
        raise Wrong(
            f"{named} isn't kept, as its decision {more.decision} isn't under {more.deliverable};"
            " take it back to the deliverable whose decision it changes"
        )
    if not _DECISION.match(more.decision) or _at(now, more.decision) is None:
        raise Wrong(f"the design tree holds no decision at {more.decision}")
    if _at_cut(at_cut, more.deliverable, more.decision[len(tree_path) :]) == _at(
        now, more.decision
    ):
        raise Wrong(
            f"{named} isn't kept, as its decision {more.decision} didn't change since the round's"
            " cut; change the decision it comes from"
        )


def _tree_path(tree: DesignTree, deliverable: str) -> str | None:
    """The path in the tree of the deliverable at the file path, or None where the tree holds
    none."""
    for number, each in enumerate(deliverables(tree)):
        if each["path"] == deliverable:
            return f"deliverables/{number}"
    return None


def _at_cut(at_cut: DesignTree, deliverable: str, under: str) -> Any:
    """The decision at the path under the deliverable in the round's cut, or None where the cut
    holds none, found by the deliverable's file path, as a deliverable added or taken out before it
    since moves its place in the list. The cut holds the deliverable, as its round opened on it."""
    tree_path = _tree_path(at_cut, deliverable)
    assert tree_path is not None, f"the round's cut holds no deliverable {deliverable}"
    return _at(at_cut, tree_path + under)


def _at(tree: DesignTree, path: str) -> Any:
    """The node at the path of a decision in the tree, or None where it holds none."""
    held: Any = tree.data
    for part in path.split("/"):
        held = held.get(part) if isinstance(held, dict) else _item(held, int(part))
    return held


def _item(held: Any, number: int) -> Any:
    """The item of the number in a list, or None where it holds none."""
    return held[number] if isinstance(held, list) and number < len(held) else None
