"""Decides where each Round and each Fix of a deliverable lies in the run's folder and what it
holds: `rounds/<step>/<deliverable>/<stage>-<n>/`, `<step>` the number of the step that makes or
adds to the deliverable, so that a later step that adds to it starts its own Rounds, the
deliverable's path percent-encoded whole, so that no two paths share a folder, `<stage>`
`content` or `refactor` for a Round and `fix` for a Fix, and
`<n>` its number among the deliverable's Rounds and Fixes, from 1 in the order made; each holding
the role's result, and a Fix its problem in `problem.md`."""

from __future__ import annotations

import os
import re
from typing import Any, NamedTuple

import form

# The stages of a deliverable's course, as each folder's name begins.
CONTENT = "content"
REFACTOR = "refactor"
FIX = "fix"
# Each role's result in a folder, by its file's name, with the schema it holds to.
RESULTS = {
    "generator": ("generator.json", "generator-round.schema.json"),
    "evaluator": ("evaluator.json", "evaluator-round.schema.json"),
    "refactorer": ("refactorer.json", "generator-round.schema.json"),
    "fixer": ("fixer.json", "fixer-fix.schema.json"),
}
_NAMED = re.compile(rf"({CONTENT}|{REFACTOR}|{FIX})-([1-9][0-9]*)")


class Entry(NamedTuple):
    """One Round or Fix of a deliverable: its stage, its number, its folder, and each role's
    result that it holds, by the role."""

    stage: str
    number: int
    folder: str
    results: dict[str, dict[str, Any]]


def entries(root: str, schemas: str) -> list[Entry]:
    """Each Round and Fix of the deliverable in the step, in the order made.

    Takes: the folder of the deliverable's Rounds and Fixes in the step, as `folder_of` gives it,
    and the folder of rn's schemas.
    Gives: each, read from its folder, each result checked against its schema; none where the
    deliverable has none yet.
    Changes: nothing.
    Refuses: Wrong where a result leaves its form, as `form.held` names it.
    """
    names = os.listdir(root) if os.path.isdir(root) else []
    found = sorted((int(m[2]), m[1], name) for name in names if (m := _NAMED.fullmatch(name)))
    return [
        _read(os.path.join(root, name), stage, number, schemas) for number, stage, name in found
    ]


def _read(folder: str, stage: str, number: int, schemas: str) -> Entry:
    results = {}
    for role, (file, schema) in RESULTS.items():
        path = os.path.join(folder, file)
        if os.path.isfile(path):
            results[role] = form.held(path, os.path.join(schemas, schema), f"the {role}'s result")
    return Entry(stage, number, folder, results)
