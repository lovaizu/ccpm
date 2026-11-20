"""Decides whether a role's result holds what its Cut gave it, beyond what a rule of Lane's holds:
its form, each condition answered once by its ID, and each line it quotes standing in the
deliverable."""

from __future__ import annotations

from rounds.files import Result
from tree.cut import Cut


def faults(role: str, cut: Cut, result: Result, worktree: str) -> list[str]:
    """Each fault of the role's result, in a line that says how to mend it.

    Takes: `generator` or `evaluator`, the role's Cut, its result, and the run's worktree.
    Gives: each place where the result leaves `<role>-round.schema.json`; for the generator, each
    `good` whose condition the Cut's deliverable doesn't hold, a `point` with no words where the
    result is `point`, and each file it names outside the deliverable's paths and the Round's
    folder; for the evaluator, each condition of the Cut answered in neither `good` nor `more`, or
    in both, or twice, and each ID the Cut doesn't hold; for both, each line of a `good` that no
    file of the deliverable holds as it stands. None where the result holds each.
    Changes: nothing.
    Refuses: Wrong where the role is neither `generator` nor `evaluator`.
    """
    raise NotImplementedError("check.result.faults")
