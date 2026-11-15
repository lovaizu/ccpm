"""Decides the Cut of each start of a role: which deliverable doing it takes, and which part of the
design tree, the best practices, the More kept, and the Place it starts with, in the form of the
role's in-schema, so that it reads no decision that's not its own."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from tree.design import DesignTree
from tree.runs import Run


@dataclass(frozen=True)
class Cut:
    """What one start of a role takes: the role, its run values, which the guard holds it to, its
    record's path among them, and the part of the design tree that it reads, in the form of
    `<role>-in.schema.json`."""

    role: str
    values: Mapping[str, str]
    part: Mapping[str, object]


def next_start(
    run: Run, tree: DesignTree, role: str, running: Sequence[Mapping[str, str]]
) -> Cut | None:
    """The Cut of the next start of a role.

    Takes: the run, its design tree, the role, and the run values of each start that runs.
    Gives: for the tree-keeper, the Cut of the run's design tree; for the generator or an evaluator,
    the Cut of the first deliverable doing, or of its first group of necessary conditions, that no
    start that runs holds, at the step its Place names where it stood in one; each with the path
    of a new record from `records.new_record`; or None where no work waits.
    Changes: nothing.
    Refuses: fault.Wrong, where the role is none of rn's.
    Carries: S1 `A->>T: gets each deliverable doing, and the Cut of the first that no start that
    runs holds, with the path of a new Record for the start (Cut)`.
    """
    raise NotImplementedError("cut.next_start")


def of_record(run: Run, record: str) -> Cut:
    """The Cut that a start took, by its record.

    Takes: the run, and the start's record.
    Gives: the Cut, as the design tree that the start's round took it from gives it.
    Changes: nothing.
    Refuses: fault.Wrong, where the record names no start of the run.
    Carries: S1 `GD->>R: checks its record, its result, and the deliverable`, as record.py gets the
    Cut of the role it checks from tree.py's code.
    """
    raise NotImplementedError("cut.of_record")
