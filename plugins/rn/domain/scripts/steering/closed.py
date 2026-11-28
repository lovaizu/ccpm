"""Decides how the work keeps its closed tasks, at `closed.json` beside its steering: each task
that a role's result completed or the orchestrator's aim canceled, in the order it closed, so that
each id in `tasks/` names a task once the steering no longer holds it."""

from __future__ import annotations

import json
import os
from typing import Any

import form
from place import WorkPlace


def held(work: WorkPlace, schemas: str) -> list[dict[str, Any]]:
    """The work's closed tasks.

    Takes: the work, and the folder of rn's schemas.
    Gives: each closed task, in the order it closed; none where no task has closed yet.
    Changes: nothing.
    Refuses: Wrong where closed.json isn't JSON or leaves its schema, as `form.held` names it.
    """
    if not os.path.isfile(work.closed):
        return []
    found = form.held(work.closed, os.path.join(schemas, "closed.schema.json"), "closed tasks")
    return list(found["tasks"])


def added(work: WorkPlace, tasks: list[dict[str, Any]], schemas: str) -> None:
    """Adds the tasks to the work's closed tasks, after those already there.

    Takes: the work, each task that closed, in its order, and the folder of rn's schemas.
    Gives: nothing.
    Changes: writes closed.json where a task is given.
    Refuses: Wrong where closed.json isn't JSON or leaves its schema, as `held` does.
    """
    if not tasks:
        return
    with_them = {"tasks": [*held(work, schemas), *tasks]}
    with open(work.closed, "w", encoding="utf-8") as f:
        json.dump(with_them, f, indent=2, ensure_ascii=False)
        f.write("\n")
