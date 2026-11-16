"""Decides which items a role's result must name: for a generator's Made, each decision of its Cut
and each More kept; for an evaluator's Answers, each necessary condition of its group; for the
tree-keeper, each node that tree.py said the change touches."""

from __future__ import annotations

from typing import Any, cast

from tree.cut import Cut
from tree.results import Answers, Made


def lacks(cut: Cut, result: str, made: Made | None, answers: Answers | None) -> tuple[str, ...]:
    """What a result leaves out of the items its Cut carries.

    Takes: the start's Cut, the result given, and the Made or Answers it wrote, or None where it
    wrote none.
    Gives: each item that the result names nowhere, said so that the role takes it: for a
    generator, each decision of its Cut by its path and each More kept by its best practice and
    condition, which key it, that its Made names no place for; for an evaluator, each condition of
    its group that its Answers answer neither good nor more; none where it names each, where the
    result is asks or lacks, or for the tree-keeper, whose reply the check doesn't read.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `R-->>GD: each step, practice, or item they lack`.
    """
    if result in ("asks", "lacks"):
        return ()
    if cut.role == "generator":
        return _made(cut, made)
    if cut.role == "evaluator":
        named = set(answers.good) | set(answers.more) if answers else set()
        conditions = cast(Any, cut.part)["conditions"]
        return tuple(f"the Answers answer no {c}" for c in conditions if c not in named)
    return ()


def _made(cut: Cut, made: Made | None) -> tuple[str, ...]:
    """Each decision and More kept of the generator's Cut that its Made names no place for, each
    More kept by its best practice and condition."""
    raise NotImplementedError("items.lacks of a generator")
