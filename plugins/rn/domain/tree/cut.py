"""Decides what each role's Cut holds: for the generator, the deliverable, its kind's or the
refactor best practice, the goal, and the decisions of its node and of each input node with no
file; for an evaluator, the deliverable, its people's aim, and the conditions of its group."""

from __future__ import annotations

from tree.course import Due
from tree.design import Tree


def write(run: str, tree: Tree, due: Due) -> str:
    """Writes the Cut of a start due.

    Takes: the run's folder, the design tree, and the start due.
    Gives: the path of the Cut written, as rounds.path names it.
    Changes: the run's folder, by the Cut, in the form of `schemas/cut.schema.json`.
    Refuses: Wrong where the start names a deliverable or a group that the tree doesn't hold."""
    raise NotImplementedError("cut.write")
