"""Decides which faults keep a change of the design tree from its commit: the tree's schema, and
each condition of the design tree best practice that code can check."""

from __future__ import annotations

from collections.abc import Mapping

from practice import Practice

from tree.form import Tree


def faults(tree: Tree, practices: Mapping[str, Practice], worktree: str) -> list[str]:
    """Each fault of the design tree, in a line that says where and how to mend it.

    Takes: the tree, the best practice of each kind by its name, as `practice.kinds` finds them,
    and the run's worktree.
    Gives: each place, by its JSON Pointer, where the tree leaves its schema; where a deliverable's
    kind is no kind of `practices`; where an open deliverable's necessary conditions aren't its
    best practice's, in their order; where an input names neither a deliverable's path nor a file
    of the worktree; where a deliverable rests on itself through its inputs; and where an item of
    `work` names no deliverable, or a `decide` names no condition or `about` of it. None where the
    tree holds each.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("tree.checks.faults")
