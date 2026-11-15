"""Decides where the record of each start of a role and the orchestrator's lie in a run's
`records/`, and the order of the starts that their names keep."""

from __future__ import annotations

from collections.abc import Sequence

from tree.runs import Run


def new_record(run: Run, role: str, taken: Sequence[str]) -> str:
    """The path of the record of a new start of a role.

    Takes: the run, the role, and the record of each start that runs, which may hold no entry yet.
    Gives: the record's path, after every record the run holds and every one taken, in the order of
    the starts.
    Changes: nothing; record.py writes the record.
    Refuses: nothing.
    Carries: S1 `A->>T: gets ... with the path of a new Record for the start`.
    """
    raise NotImplementedError("records.new_record")


def orchestrator_record(run: Run) -> str:
    """The path of the orchestrator's record of the run.

    Takes: the run.
    Gives: the record's path.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `O->>T: makes the run's worktree`, which gives the orchestrator its record; S5
    `O->>T: lists the runs left`.
    """
    raise NotImplementedError("records.orchestrator_record")


def in_order(run: Run) -> tuple[str, ...]:
    """The record of each start of a role in the run, in the order of the starts.

    Takes: the run.
    Gives: each record's path.
    Changes: nothing.
    Refuses: nothing.
    Carries: S5 `A->>T: gets ... each Record of the run in the order of its starts (Record)`.
    """
    raise NotImplementedError("records.in_order")


def role_of(record: str) -> str:
    """The role whose start a record keeps.

    Takes: the record's path.
    Gives: the role, from the record's name.
    Changes: nothing.
    Refuses: fault.Wrong, where the path names no record of a run.
    Carries: S5 `A-->>GD: those results in Lane's form`, each by its role; S1 `G->>T: commits its
    work at the end of each step (Place)`, which names the start by its record.
    """
    raise NotImplementedError("records.role_of")
