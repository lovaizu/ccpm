"""Decides what rn's check holds an end to: a role's record against its prompt's steps and its best
practices, its result against the items of its Cut, and its deliverable against its kind's
template; the orchestrator's record at the end of a turn that puts work up."""

from __future__ import annotations


def check(
    plugin_root: str, cwd: str, role: str, result: str, record: str | None
) -> tuple[str, ...]:
    """What an end lacks.

    Takes: rn's folder; the folder the end came from; the role, or orchestrator; the result given,
    empty where none was; and the start's record, or None for the orchestrator's of the run of the
    folder.
    Gives: each step, practice, or item lacking, from `order.lacks` and `items.lacks`, and each
    place where the deliverable leaves its kind's template, from template.check, with the Cut,
    Made, Answers, and best practice from tree.py's code; none where it lacks nothing, or where
    the orchestrator's turn puts no work up.
    Changes: keeps the result in the record through `form.keep` once it lacks nothing.
    Refuses: fault.Wrong, where the record or a file it reads leaves its form; fault.CantRun, where
    one can't be read.
    Carries: S1 `GD->>R: checks its record, its result, and the deliverable (Record)`, and `R-->>GD:
    each step, practice, or item they lack, and each place where the deliverable leaves its kind's
    template, or none, keeping the result in the record`.
    """
    raise NotImplementedError("check.check")
