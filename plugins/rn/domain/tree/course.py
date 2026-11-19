"""Decides the course of a deliverable's Rounds: which start is due, whether a Round makes the
content by the kind's best practice or refactors it by the refactor best practice, the limit of two
Rounds of each since the deliverable's latest sign-off sent it back, and the groups a later Round
judges, those holding a condition whose decisions changed."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from tree.design import Tree
from tree.rounds import Start


@dataclass(frozen=True)
class Due:
    """A start due: the deliverable's path, its role, the group an evaluator judges or "" for the
    generator, the best practice its Round works by, and the Round's number."""

    deliverable: str
    role: str
    group: str
    best_practice: str
    round: int


def due(tree: Tree, starts: Sequence[Start], running: Sequence[Due]) -> Sequence[Due]:
    """Each start due, beside those that run.

    Takes: the design tree, each start of the run's Rounds, and each start that runs.
    Gives: the generator of the first deliverable of `work` whose inputs are done, where its
    latest Round has no result of the generator or its evaluators judged it short within the limit;
    or one evaluator for each group due once the generator gave its result; or none where no Round
    is due, such as while a point or a sign-off waits.
    Refuses: nothing."""
    raise NotImplementedError("course.due")


def left(tree: Tree, starts: Sequence[Start], deliverable: str) -> Sequence[str]:
    """Each finding of the deliverable's latest Round that the limit leaves, to go to the user as a
    proposal.

    Takes: the design tree, each start of the run's Rounds, and the deliverable's path.
    Gives: each `more` of its evaluators past two Rounds of content or of refactoring; none within
    the limit.
    Refuses: nothing."""
    raise NotImplementedError("course.left")
