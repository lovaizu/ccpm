"""Decides what waits for the user's sign-off, and what a sign-off changes in the design tree: an
open deliverable, the plan among them, waits once its Rounds are over, and once signed off it is
done."""

from __future__ import annotations

from collections.abc import Mapping

from rounds.course import Next

from tree.form import Tree


def waiting(tree: Tree, nexts: Mapping[str, Next]) -> str | None:
    """The deliverable that waits for the user's sign-off.

    Takes: the tree, and what each open deliverable that Rounds make waits on, by its path, as
    `rounds.course.next_of` gives it.
    Gives: the path of the plan, the deliverable of the kind `design-tree`, where it's open with
    each condition good; else of the first deliverable in the tree's order that's open with each
    condition good and waits on the sign-off; None where none does.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("tree.signoff.waiting")


def signed_off(tree: Tree, deliverable: str) -> Tree:
    """The design tree once the user signs the deliverable off.

    Takes: the tree, and the deliverable's path.
    Gives: the tree with the deliverable done, keeping its name, path, more_paths, and kind, or,
    for a node with no file, its necessary conditions too; and without each item of `work` that
    names it.
    Changes: nothing.
    Refuses: Wrong where no open deliverable has the path, or one of its conditions isn't good.
    """
    raise NotImplementedError("tree.signoff.signed_off")
