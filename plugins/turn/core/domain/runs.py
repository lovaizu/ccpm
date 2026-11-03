"""The run values of each run of a step, read from the run's folder: one run of builder for each
part of the work, only those a remake reaches where there is one; one of evaluator or proofreader
for each group of questions; and one of refactorer. The role before the step hands them to up, as
Lane lets up make no call but the start due once a step has ended."""

from __future__ import annotations

import os
from typing import Any, Callable

import files

# The groups and the standard of evaluator and of proofreader, and the folder of their answers.
READERS = {
    "evaluator": ("groups", "standard.json", "verification"),
    "proofreader": ("refactoring_groups", "refactoring-standard.json", "proofreading"),
}


def builders(run: str, work: dict[str, Any], common: dict[str, Any]) -> list[dict[str, Any]]:
    """A run of builder for each part, only the parts a remake reaches where there is one."""
    remake = os.path.join(run, "remake.json")
    again = (
        {d["decision"] for d in files.load(remake, "remake")["decisions"]}
        if os.path.exists(remake)
        else None
    )
    return [
        {
            **common,
            "work": p["paths"],
            "decisions": p["decisions"],
            "answers": f"{run}/self-check/{p['id']}.json",
            "open": f"{run}/open/{p['id']}.json",
        }
        for p in work["parts"]
        if again is None or again & set(p["decisions"])
    ]


def refactorers(run: str, work: dict[str, Any], common: dict[str, Any]) -> list[dict[str, Any]]:
    """The one run of refactorer."""
    return [{**common, "answers": f"{run}/refactor-check.json"}]


def readers(role: str) -> Callable[[str, dict[str, Any], dict[str, Any]], list[dict[str, Any]]]:
    """The runs of evaluator or of proofreader, one for each group of their questions."""
    key, standard, folder = READERS[role]

    def found(run: str, work: dict[str, Any], common: dict[str, Any]) -> list[dict[str, Any]]:
        path = os.path.join(run, "run.json")
        groups = files.load(path, "run").get(key)
        if groups is None:
            raise files.Unreadable(f"{path} has no {key} yet")
        return [
            {
                **common,
                "questions": g["questions"],
                "standard": f"{run}/{standard}",
                "answers": f"{run}/{folder}/{g['id']}.json",
            }
            for g in groups
        ]

    return found


STEPS = {
    "builder": builders,
    "evaluator": readers("evaluator"),
    "refactorer": refactorers,
    "proofreader": readers("proofreader"),
}
ROLES = tuple(STEPS)


def runs(run: str, role: str) -> list[dict[str, Any]]:
    """The values of each run of the role's step, in the order of the parts or groups; refuses, by
    files.Unreadable, a role that has no step of runs, and a file it cannot read."""
    if role not in STEPS:
        raise files.Unreadable(
            f"{role} is not builder, evaluator, refactorer or proofreader, whose runs this gives"
        )
    work = files.load(os.path.join(run, "work.json"), "work")
    common = {"run": run, "work": work["paths"], "commands": work["commands"]}
    return STEPS[role](run, work, common)
