"""Decides each role's Cut, the part of the design tree that the role starts with and nothing else,
and the run values that the guard holds the role to: the tree-keeper's design tree; the
generator's goal, deliverable, decisions, inputs, the lacks kept for its round, the step it stood
at, and the refactor best practice that finishes its deliverable; and the evaluator's deliverable,
its people, and one group of necessary conditions."""

from __future__ import annotations

from dataclasses import dataclass

from tree.design import Decision
from tree.rounds import LackKept, Place

TREE_KEEPER, GENERATOR, EVALUATOR = "tree-keeper", "generator", "evaluator"


@dataclass(frozen=True)
class Cut:
    """One role's Cut, as `tree.py cut` writes it into the run's folder: the role, the run's folder,
    the role's record, and what the role's `<role>-in.schema.json` names beside them, each "" or
    empty where the role takes none: the design tree's path for the tree-keeper; the deliverable,
    its kind, its best practice, the round, the goal, the decisions it builds from, its inputs, the
    lacks kept, the Place it picks up from, the path of the refactor best practice that finishes
    the deliverable, and where it writes what it made, for the generator;
    and the deliverable, its best practice, the round, the goal, who its people are, the group, its
    necessary conditions, and where it writes its Answers, for the evaluator."""

    role: str
    run: str
    record: str
    tree: str = ""
    deliverable: str = ""
    kind: str = ""
    best_practice: str = ""
    round: int = 0
    goal: str = ""
    decisions: tuple[Decision, ...] = ()
    inputs: tuple[str, ...] = ()
    lacks: tuple[LackKept, ...] = ()
    place: Place | None = None
    finish: str = ""
    group: str = ""
    conditions: tuple[str, ...] = ()
    out: str = ""
    path: str = ""


def cut(run: str, role: str, deliverable: str = "", group: str = "") -> Cut:
    """The Cut of the role for its next start in the run: the tree-keeper's on the run alone; the
    generator's on the deliverable, in its round that a Place shows a generator stood in, or else
    in a new round after its last; the evaluator's on the deliverable's last round and the group.
    Raises Wrong, with what it takes, where the role is none of rn's, the deliverable isn't one
    doing in the tree, or the group isn't one of its best practice's."""
    raise NotImplementedError("cut.cut")


def save(cut: Cut) -> Cut:
    """Writes the Cut into the run's folder, in its round's folder for a generator or an evaluator,
    and gives it with its path and its record's path filled in, the record a new file of
    `records/` for each start."""
    raise NotImplementedError("cut.save")


def load(path: str) -> Cut:
    """The Cut that `save` wrote to the file at the path. Raises Wrong where it isn't one."""
    raise NotImplementedError("cut.load")


def values(cut: Cut) -> dict[str, str]:
    """The run values of the Cut, as its role's `<role>-in.schema.json` names them under `start`,
    each a string."""
    raise NotImplementedError("cut.values")
