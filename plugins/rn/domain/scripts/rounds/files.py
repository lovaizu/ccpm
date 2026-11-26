"""Decides where each Round and each Fix of a deliverable lies in the run's folder and what it
holds: `rounds/<step>/<deliverable>/<stage>-<n>/`, `<step>` the number of the step that makes or
adds to the deliverable, so that a later step that adds to it starts its own Rounds, the
deliverable's path percent-encoded whole, so that no two paths share a folder, `<stage>`
`content` or `refactor` for a Round and `fix` for a Fix, and
`<n>` its number among the deliverable's Rounds and Fixes, from 1 in the order made; each holding
`start.json`, how many decisions the run held when it started, then the role's result, and
`weighed.json` once a pruner weighed it, and a Fix its problem in `problem.md`."""

from __future__ import annotations

import json
import os
import re
from typing import Any, NamedTuple
from urllib.parse import quote

import form
from fault import Wrong
from place import RunPlace

# The stages of a deliverable's course, as each folder's name begins.
CONTENT = "content"
REFACTOR = "refactor"
FIX = "fix"
# Each role's result in a folder, by its file's name, with the schema it holds to.
RESULTS = {
    "generator": ("generator.json", "generator-round.schema.json"),
    "evaluator": ("evaluator.json", "evaluator-round.schema.json"),
    "fixer": ("fixer.json", "fixer-fix.schema.json"),
}
_NAMED = re.compile(rf"({CONTENT}|{REFACTOR}|{FIX})-([1-9][0-9]*)")


class Entry(NamedTuple):
    """One Round or Fix of a deliverable: its stage, its number, its folder, how many decisions the
    run held when it started, each role's result that it holds, by the role, and whether a pruner
    weighed it."""

    stage: str
    number: int
    folder: str
    decisions: int
    results: dict[str, dict[str, Any]]
    weighed: bool


def folder_of(run: RunPlace, step: int, deliverable: str) -> str:
    """The folder of the deliverable's Rounds and Fixes in the step."""
    return os.path.join(run.rounds, str(step), quote(deliverable, safe=""))


def entries(root: str, schemas: str) -> list[Entry]:
    """Each Round and Fix of the deliverable in the step, in the order made.

    Takes: the folder of the deliverable's Rounds and Fixes in the step, as `folder_of` gives it,
    and the folder of rn's schemas.
    Gives: each, read from its folder, each result checked against its schema; none where the
    deliverable has none yet.
    Changes: nothing.
    Refuses: Wrong where a result or `start.json` leaves its form, as `form.held` names it.
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
    with open(os.path.join(folder, "start.json"), encoding="utf-8") as f:
        decisions = json.load(f)["decisions"]
    weighed = os.path.isfile(os.path.join(folder, "weighed.json"))
    return Entry(stage, number, folder, decisions, results, weighed)


def started(root: str, stage: str, decisions: int, made: list[Entry]) -> str:
    """Makes the deliverable's next Round or Fix of the stage in the step, and gives its folder.

    Takes: the folder of the deliverable's Rounds and Fixes in the step, as `folder_of` gives it,
    the stage, how many decisions the run holds now, and its Rounds and Fixes there so far.
    Gives: the new folder, numbered one past the last.
    Changes: makes the folder, holding `start.json` with the decisions' count.
    Refuses: nothing.
    """
    number = made[-1].number + 1 if made else 1
    folder = os.path.join(root, f"{stage}-{number}")
    os.makedirs(folder)
    with open(os.path.join(folder, "start.json"), "w", encoding="utf-8") as f:
        json.dump({"decisions": decisions}, f)
        f.write("\n")
    return folder


def weigh(run: RunPlace, folder: str) -> None:
    """Marks a Round or Fix as weighed by a pruner.

    Takes: the run, and the folder of a Round or Fix.
    Gives: nothing.
    Changes: writes `weighed.json` in it.
    Refuses: Wrong where the folder isn't a Round's or a Fix's of the run.
    """
    within = os.path.relpath(os.path.normpath(folder), run.rounds).split(os.sep)
    shaped = len(within) == 3 and within[0].isdigit() and _NAMED.fullmatch(within[2])
    if not shaped or not os.path.isdir(folder):
        raise Wrong(f"{folder}: isn't a Round's or a Fix's folder of the run")
    with open(os.path.join(folder, "weighed.json"), "w", encoding="utf-8") as f:
        f.write("{}\n")
