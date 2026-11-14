"""Decides the form of a run's design tree, `design-tree.json` in the run's folder, as
`design-tree.schema.json` of the design tree best practice gives it: the goal, each deliverable with
its necessary conditions and decisions, and the order of the deliverables, each after the
deliverables it takes from and waits for."""

from __future__ import annotations

from dataclasses import dataclass

DESIGN_TREE = "design-tree.json"
# Where a deliverable stands, and the kind of a deliverable of this product alone.
OPEN, DOING, DONE = "open", "doing", "done"
SPECIFIC = "specific"
# Who settled a point, as the schema's `by` names them.
BY = ("user", "maker", "reasoning", "research")


@dataclass(frozen=True)
class Decision:
    """A decision of the design tree: the point it settles, what holds for it, None while it's
    open, which the data model calls a Point, and who settled it, "" while it's open."""

    about: str
    decided: str | None
    by: str = ""


@dataclass(frozen=True)
class NecessaryCondition:
    """A necessary condition of the deliverable's best practice, by its ID, whether the deliverable
    meets it, and the decisions that answer it."""

    id: str
    good: bool = False
    decisions: tuple[Decision, ...] = ()


@dataclass(frozen=True)
class Deliverable:
    """A deliverable of the design tree: its name, its path, its kind, its status, the paths it
    takes from and waits for, and the necessary conditions of its best practice; for a `specific`
    one, the check that judges it, whether it passes, and its decisions in place of conditions. A
    deliverable done keeps only its name, path, kind, and status."""

    name: str
    path: str
    kind: str
    status: str = OPEN
    inputs: tuple[str, ...] = ()
    preconditions: tuple[str, ...] = ()
    conditions: tuple[NecessaryCondition, ...] = ()
    check: str = ""
    good: bool = False
    decisions: tuple[Decision, ...] = ()


@dataclass(frozen=True)
class DesignTree:
    """The design tree: the goal, as one sentence with the user as its subject, who settled it, and
    the deliverables in the order of the work."""

    goal: str
    by: str
    deliverables: tuple[Deliverable, ...] = ()


@dataclass(frozen=True)
class Point:
    """A decision of the tree still open, with the deliverable and the necessary condition it lies
    under, "" for a `specific` deliverable's own decision."""

    deliverable: str
    condition: str
    decision: Decision


def loads(text: str, where: str) -> DesignTree:
    """The design tree of the JSON text read from the file at `where`. Raises Wrong, naming the
    file, the field, and what the schema takes there, where the text isn't in the form of
    `design-tree.schema.json`."""
    raise NotImplementedError("design.loads")


def dumps(tree: DesignTree) -> str:
    """The design tree as the JSON text of `design-tree.json`, which `loads` reads back as it
    was."""
    raise NotImplementedError("design.dumps")


def load(run: str) -> DesignTree | None:
    """The design tree of the run's folder, or None where the run has none yet. Raises Wrong as
    `loads` does."""
    raise NotImplementedError("design.load")


def save(run: str, tree: DesignTree) -> None:
    """Writes the design tree into the run's folder as `dumps` gives it."""
    raise NotImplementedError("design.save")


def order_faults(tree: DesignTree) -> tuple[str, ...]:
    """Each fault of the tree's order, as the design tree best practice asks a script to check after
    each change: a deliverable before one it takes from or waits for, a path of inputs or
    preconditions that's neither a deliverable of the tree nor a file of the worktree, and two
    deliverables at one path. None where the order holds."""
    raise NotImplementedError("design.order_faults")


def points(tree: DesignTree) -> tuple[Point, ...]:
    """Each decision of the tree still open, in the order of the tree."""
    raise NotImplementedError("design.points")


def deliverable(tree: DesignTree, path: str) -> Deliverable | None:
    """The deliverable of the tree at the path, or None where the tree holds none there."""
    raise NotImplementedError("design.deliverable")
