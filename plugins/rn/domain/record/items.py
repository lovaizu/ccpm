"""Decides which items a role's result must name: for a generator's Made, each decision of its Cut
and each More kept; for an evaluator's Answers, each necessary condition of its group; for the
tree-keeper, each node that tree.py said the change touches."""

from __future__ import annotations

from tree.cut import Cut
from tree.results import Answers, Made


def lacks(cut: Cut, result: str, made: Made | None, answers: Answers | None) -> tuple[str, ...]:
    """What a result leaves out of the items its Cut carries.

    Takes: the start's Cut, the result given, and the Made or Answers it wrote, or None where its
    role writes neither.
    Gives: each item that the result names nowhere, said so that the role takes it; none where it
    names each, or where the result is asks or lacks.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `R-->>GD: each step, practice, or item they lack`.
    """
    raise NotImplementedError("items.lacks")
