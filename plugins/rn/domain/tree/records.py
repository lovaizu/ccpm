"""Decides where the record of each start of a role and the orchestrator's lie in a run's
`records/`, and the order of the starts that their names keep."""

from __future__ import annotations

import os
import re
from collections.abc import Sequence

from fault import Wrong

from tree.runs import Run

# A record's name: the start's number in the order of the starts, its role, and, for a start of a
# round, which start of the round it is, as tree/rounds.py names it; or the orchestrator's.
_NAME = re.compile(r"^(\d+)-(tree-keeper|generator|evaluator)(?:\.([^/]+))?\.json$")
_ORCHESTRATOR = "orchestrator.json"


def new_record(run: Run, role: str, taken: Sequence[str], start: str = "") -> str:
    """The path of the record of a new start of a role.

    Takes: the run, the role, the record of each start that runs, which may hold no entry yet, and,
    for a start of a round, which start of the round it is, as `start_of` gives it back.
    Gives: the record's path from the worktree, after every record the run holds and every one
    taken, in the order of the starts.
    Changes: nothing; record.py writes the record.
    Refuses: nothing.
    Carries: S1 `A->>T: gets ... with the path of a new Record for the start`.
    """
    numbers = [int(found[1]) for found in map(_NAME.match, _names(run, taken)) if found]
    name = f"{max(numbers, default=0) + 1:03d}-{role}{'.' + start if start else ''}.json"
    return os.path.relpath(os.path.join(run.folder, "records", name), run.worktree)


def orchestrator_record(run: Run) -> str:
    """The path of the orchestrator's record of the run.

    Takes: the run.
    Gives: the record's path.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `O->>T: makes the run's worktree`, which gives the orchestrator its record; S5
    `O->>T: lists the runs left`.
    """
    return os.path.relpath(os.path.join(run.folder, "records", _ORCHESTRATOR), run.worktree)


def in_order(run: Run) -> tuple[str, ...]:
    """The record of each start of a role in the run, in the order of the starts.

    Takes: the run.
    Gives: each record's path.
    Changes: nothing.
    Refuses: nothing.
    Carries: S5 `A->>T: gets ... each Record of the run in the order of its starts (Record)`.
    """
    folder = os.path.join(run.folder, "records")
    return tuple(
        os.path.relpath(os.path.join(folder, name), run.worktree)
        for name in sorted(_names(run, ()))
        if _NAME.match(name)
    )


def role_of(record: str) -> str:
    """The role whose start a record keeps.

    Takes: the record's path.
    Gives: the role, from the record's name.
    Changes: nothing.
    Refuses: fault.Wrong, where the path names no record of a run.
    Carries: S5 `A-->>GD: those results in Lane's form`, each by its role; S1 `G->>T: commits its
    work at the end of each step (Place)`, which names the start by its record.
    """
    return _parts(record)[0]


def start_of(record: str) -> str:
    """Which start of a round a record keeps.

    Takes: the record's path.
    Gives: the start of the round, as `new_record` took it, or "" for a start of no round.
    Changes: nothing.
    Refuses: fault.Wrong, where the path names no record of a run.
    Carries: S1 `GD->>R: checks its record`, by the Cut of the start, and `G->>T: commits its work
    at the end of each step (Place)`, in the round of the start.
    """
    return _parts(record)[1]


def _parts(record: str) -> tuple[str, str]:
    """The role and the start of a round of a record, by its name in a run's records/."""
    name = os.path.basename(record)
    found = _NAME.match(name)
    in_records = os.path.basename(os.path.dirname(record)) == "records"
    if in_records and name == _ORCHESTRATOR:
        return "orchestrator", ""
    if not (in_records and found):
        raise Wrong(f"{record!r} names no record of a run, which lies in its records/")
    return found[2], found[3] or ""


def _names(run: Run, taken: Sequence[str]) -> list[str]:
    """The name of each record that the run's records/ holds, and of each one taken."""
    folder = os.path.join(run.folder, "records")
    held = os.listdir(folder) if os.path.isdir(folder) else []
    return held + [os.path.basename(each) for each in taken]
