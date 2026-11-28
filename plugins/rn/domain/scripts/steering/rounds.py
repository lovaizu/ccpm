"""Decides where each Round and each Fix of a task lies in the work's folder and what it holds:
`tasks/<id>/<nn>-<stage>/`, `<id>` the task's, `<nn>` its number among the task's Rounds and Fixes,
two digits from 01 in the order made, first so that they list in that order, and `<stage>`
`content` or `refactor` for a Round and `fix` for a Fix; each holding the role's result, and a Fix
its problem in `problem.md`."""

from __future__ import annotations

import glob
import os
import re
from typing import Any, NamedTuple

import form
from fault import Wrong
from place import WorkPlace

# The stages of a deliverable's course, as each folder's name begins.
CONTENT = "content"
REFACTOR = "refactor"
FIX = "fix"
# Each role's result in a folder, by its file's name, with the schema it holds to.
RESULTS = {
    "generator": ("generator.json", "generator-round.schema.json"),
    "evaluator": ("evaluator.json", "evaluator-round.schema.json"),
    "refactorer": ("refactorer.json", "generator-round.schema.json"),
    "fixer": ("fixer.json", "generator-round.schema.json"),
}
_NAMED = re.compile(rf"([0-9]{{2,}})-({CONTENT}|{REFACTOR}|{FIX})")


class Entry(NamedTuple):
    """One Round or Fix of a task: its stage, its number, its folder, and each role's
    result that it holds, by the role."""

    stage: str
    number: int
    folder: str
    results: dict[str, dict[str, Any]]


def folder_of(work: WorkPlace, task: str) -> str:
    """The folder of the Rounds and Fixes of the task of the id."""
    return os.path.join(work.tasks, task)


def named(number: int, stage: str) -> str:
    """The name of the Round or Fix of the number and stage, as `entries` reads it."""
    return f"{number:02d}-{stage}"


def faults(work: WorkPlace, schemas: str) -> list[str]:
    """Each result of the work that leaves its schema, in words, as `entries` names it; none
    where each holds."""
    found = []
    for root in sorted(glob.glob(os.path.join(work.tasks, "*"))):
        try:
            entries(root, schemas)
        except Wrong as why:
            found.append(str(why))
    return found


def entries(root: str, schemas: str) -> list[Entry]:
    """Each Round and Fix of the task, in the order made.

    Takes: the folder of the task's Rounds and Fixes, as `folder_of` gives it, and the folder of
    rn's schemas.
    Gives: each, read from its folder, each result checked against its schema; none where the
    task has none yet.
    Changes: nothing.
    Refuses: Wrong where a result leaves its form, as `form.held` names it.
    """
    names = os.listdir(root) if os.path.isdir(root) else []
    found = sorted((int(m[1]), m[2], name) for name in names if (m := _NAMED.fullmatch(name)))
    return [
        _read(os.path.join(root, name), stage, number, schemas) for number, stage, name in found
    ]


def _read(folder: str, stage: str, number: int, schemas: str) -> Entry:
    return Entry(stage, number, folder, results(folder, schemas))


def results(folder: str, schemas: str) -> dict[str, dict[str, Any]]:
    """Each role's result that a Round or Fix holds, by the role.

    Takes: the folder of the Round or Fix, and the folder of rn's schemas.
    Gives: each result there, checked against its schema; none where the folder holds none.
    Changes: nothing.
    Refuses: Wrong where a result leaves its form, as `form.held` names it.
    """
    found = {}
    for role, (file, schema) in RESULTS.items():
        path = os.path.join(folder, file)
        if os.path.isfile(path):
            found[role] = form.held(path, os.path.join(schemas, schema), f"the {role}'s result")
    return found
