"""Decides where the best practice of each kind lies and what of it each role gets: the run's own
best practices in `.rn/best-practices/<kind>/` before rn's, each read from its
`best-practice.json`, the items a maker takes at each stage, and the goal and conditions alone
that an evaluator judges by."""

from __future__ import annotations

import copy
import json
import os
from typing import Any, NamedTuple

from check.form import faults
from fault import Wrong

# rn's form of a best practice, beside this module.
_SCHEMA = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "schemas", "best-practice.schema.json"
)
_FILE = "best-practice.json"
# The kinds whose deliverables are code, refactored by refactor-code.
_CODE = {"code", "software-design", "test-design", "test-implementation"}

# A best practice as its best-practice.json holds it, in the form of
# domain/schemas/best-practice.schema.json.
Practice = dict[str, Any]


class Found(NamedTuple):
    """A kind's best practice with the folder it lies in, which a Cut names."""

    folder: str
    practice: Practice


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
    Refuses: Wrong where the file is missing, isn't JSON, or leaves rn's form of a best practice,
    `domain/schemas/best-practice.schema.json`, as `check.form.faults` holds it, naming the file
    and the first fault.
    """
    path = os.path.join(folder, _FILE)
    try:
        with open(path, encoding="utf-8") as file:
            practice = json.load(file)
    except FileNotFoundError:
        raise Wrong(f"{path}: no best practice lies there") from None
    except ValueError as error:
        raise Wrong(f"{path}: isn't JSON: {error}") from None
    found = faults(practice, _SCHEMA)
    if found:
        raise Wrong(f"{path}: leaves rn's form of a best practice at {found[0]}")
    return practice


def items(practice: Practice, at: str) -> list[str]:
    """The IDs of the items that a maker takes at a stage of the work.

    Takes: the best practice, and `decide` or `make`.
    Gives: each item's ID marked so, its condition's ID and its place from 1, such as `N1.2`, in
    the best practice's order.
    Changes: nothing.
    Refuses: Wrong where `at` is neither `decide` nor `make`.
    """
    if at not in ("decide", "make"):
        raise Wrong(f"a maker takes items at decide or make, not {at!r}")
    return [
        f"{condition['id']}.{place}"
        for condition in conditions(practice["goal"])
        for place, item in enumerate(condition["items"], 1)
        if item["at"] == at
    ]


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
