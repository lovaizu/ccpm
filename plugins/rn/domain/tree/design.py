"""Decides the design tree's form on disk, `design-tree.json` in a run's folder, as the design tree
best practice's `design-tree.schema.json` gives it: how tree.py reads it, applies a change to its
nodes by their paths, writes it, and tells what changed."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from tree.runs import Run


@dataclass(frozen=True)
class DesignTree:
    """A run's design tree: the goal, its decisions, and the plan of deliverables, as JSON in the
    design tree best practice's form."""

    data: Mapping[str, object]


@dataclass(frozen=True)
class Change:
    """What the tree-keeper writes into the tree: each node, by its path such as
    `deliverables/3/necessary_conditions/0/decisions/1`, with its new content, or None to remove
    it, such as the goal drafted, a Decision, or a Deliverable marked done once it's signed off."""

    nodes: Mapping[str, object]


def read(run: Run) -> DesignTree:
    """The run's design tree.

    Takes: the run.
    Gives: the tree in its folder.
    Changes: nothing.
    Refuses: fault.Wrong, naming each place out of form, where the file leaves the schema;
    fault.CantRun, where it can't be read.
    Carries: S1 `A->>T: gets each deliverable doing, and the Cut`, `O->>T: gets the round`, and each
    `K->>T: writes`, which read the tree first.
    """
    raise NotImplementedError("design.read")


def apply(tree: DesignTree, change: Change) -> DesignTree:
    """The tree with a change made to its nodes.

    Takes: the tree, and the change.
    Gives: the tree changed.
    Changes: nothing.
    Refuses: fault.Wrong, naming each place, where a path names no node or the tree changed leaves
    the schema.
    Carries: S1 `K->>T: writes them, and commits (Design tree)`, and `K->>T: writes the decision`;
    S2 and S3 `K->>T: writes it`.
    """
    raise NotImplementedError("design.apply")


def changed(before: DesignTree, after: DesignTree) -> tuple[str, ...]:
    """The path of each node that differs between two trees.

    Takes: the tree before and after a change.
    Gives: each path, in the order of the tree.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `T-->>K: what changed, and each node they touch`.
    """
    raise NotImplementedError("design.changed")


def write(run: Run, tree: DesignTree) -> str:
    """Writes the run's design tree.

    Takes: the run, and the tree.
    Gives: the path written, from the worktree.
    Changes: the run's design-tree.json.
    Refuses: fault.CantRun, where it can't be written.
    Carries: S1 `K->>T: writes them, and commits (Design tree)`.
    """
    raise NotImplementedError("design.write")
