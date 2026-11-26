"""Decides where the best practice of each kind lies and what of it each role gets: the run's own
best practices in `.rn/best-practices/<kind>/` before rn's, each read from its
`best-practice.json`, its template at `template.md` beside it, and the goal and conditions alone
that an evaluator judges by."""

from __future__ import annotations

import copy
import json
import os
from typing import Any

from fault import Wrong

_FILE = "best-practice.json"
# The file of a kind's template, beside its best practice.
_TEMPLATE = "template.md"
# The kinds whose deliverables are code, refactored by refactor-code.
_CODE = {"code", "software-design", "test-design", "test-implementation"}

# A best practice as its best-practice.json holds it, in the form of
# domain/schemas/best-practice.schema.json.
Practice = dict[str, Any]


def kinds(plugin_root: str, worktree: str) -> dict[str, str]:
    """The folder of each kind's best practice.

    Takes: rn's folder, and the run's worktree.
    Gives: each kind by its folder's name, to the folder of its best practice: the worktree's
    `.rn/best-practices/<kind>/` where it holds one, else rn's `domain/best-practices/<kind>/`.
    Changes: nothing.
    Refuses: nothing; a folder with no `best-practice.json` is no kind.
    """
    found: dict[str, str] = {}
    for top in (
        os.path.join(plugin_root, "domain", "best-practices"),
        os.path.join(worktree, ".rn", "best-practices"),
    ):
        if not os.path.isdir(top):
            continue
        for kind in os.listdir(top):
            folder = os.path.join(top, kind)
            if os.path.isfile(os.path.join(folder, _FILE)):
                found[kind] = folder
    return found


def read(folder: str) -> Practice:
    """The best practice in the folder.

    Takes: the folder of a kind's best practice.
    Gives: its `best-practice.json`.
    Changes: nothing.
    Refuses: Wrong where the file is missing or isn't JSON, naming the file.
    """
    path = os.path.join(folder, _FILE)
    try:
        with open(path, encoding="utf-8") as file:
            practice = json.load(file)
    except FileNotFoundError:
        raise Wrong(f"{path}: no best practice lies there") from None
    except ValueError as error:
        raise Wrong(f"{path}: isn't JSON: {error}") from None
    return practice


def template(folder: str) -> str | None:
    """The template of the best practice in the folder.

    Takes: the folder of a kind's best practice.
    Gives: the path of its `template.md`; None where the folder holds none.
    Changes: nothing.
    Refuses: nothing.
    """
    path = os.path.join(folder, _TEMPLATE)
    return path if os.path.isfile(path) else None


def judged(practice: Practice) -> dict[str, Any]:
    """What an evaluator judges by.

    Takes: the best practice.
    Gives: its goal's `what` and its critical success factors, each condition with its `id`,
    `about`, and `what` alone, leaving out each practice, as the evaluator judges what the people
    get, not how it was made.
    Changes: nothing.
    Refuses: nothing.
    """
    goal = copy.deepcopy(practice["goal"])
    for condition in conditions(goal):
        # A condition's practice is its why and its items, which its form holds beside it.
        del condition["why"], condition["items"]
    return goal


def refactoring(kind: str) -> str | None:
    """The kind of the best practice by which a deliverable of the kind is refactored.

    Takes: a deliverable's kind.
    Gives: `refactor-code` for `code`, `software-design`, `test-design`, and
    `test-implementation`; None for `light`, which its check alone makes; and `refactor-doc` for
    each other kind.
    Changes: nothing.
    Refuses: nothing.
    """
    if kind == "light":
        return None
    return "refactor-code" if kind in _CODE else "refactor-doc"


def conditions(goal: dict[str, Any]) -> list[dict[str, Any]]:
    """Each necessary condition of a best practice's goal, or of what `judged` gives, in its
    order."""
    return [
        condition
        for factor in goal["critical_success_factors"]
        for condition in factor["necessary_conditions"]
    ]
