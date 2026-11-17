"""Decides where the best practice of each kind lies for a run, the one made on a run, in
`.rn/best-practices/<kind>/` of the run's worktree, over rn's own of that kind, and which refactor
best practice and which groups of necessary conditions it gives a deliverable."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

from fault import Wrong

from tree.runs import Run


@dataclass(frozen=True)
class Group:
    """One group of necessary conditions that a deliverable is judged by, one evaluator's: the kind
    of its best practice, such as code or refactor-code, which a More kept names, the best
    practice's folder, and the ID of each condition."""

    kind: str
    folder: str
    conditions: tuple[str, ...]


def folder(run: Run, plugin_root: str, kind: str) -> str:
    """The folder of a kind's best practice.

    Takes: the run, rn's folder, and the kind, such as readme.
    Gives: the folder of the run's own best practice of the kind where it has one, or else rn's own,
    as an absolute path.
    Changes: nothing.
    Refuses: fault.Wrong, naming the kinds there are, where neither has the kind.
    Carries: S1 `A->>T: gets ... the Cut`, which names the best practice of the role's kind; and
    record.py's check, which reads that best practice's practices and template.
    """
    places = (
        os.path.join(run.worktree, ".rn", "best-practices"),
        os.path.join(os.path.realpath(plugin_root), "domain", "best-practices"),
    )
    for place in places:
        if os.path.isdir(os.path.join(place, kind)):
            return os.path.join(place, kind)
    kinds = sorted({k for p in places if os.path.isdir(p) for k in os.listdir(p)})
    raise Wrong(f"no best practice of the kind {kind!r}; the kinds are {', '.join(kinds)}")


def refactor(kind: str) -> str:
    """The kind of the refactor best practice that finishes a deliverable of the kind.

    Takes: the deliverable's kind.
    Gives: refactor-code for code, and refactor-doc for every other kind, each a document.
    Changes: nothing.
    Refuses: nothing.
    Carries: S1 `A->>T: ... the Cut`, which names the refactor best practice that the generator
    finishes by, and `par one for each group of necessary conditions, of the kind's best practice
    and of the refactor one`.
    """
    return "refactor-code" if kind == "code" else "refactor-doc"


def groups(best_practice: str) -> tuple[tuple[str, ...], ...]:
    """Each group of necessary conditions of a best practice.

    Takes: the best practice's folder.
    Gives: the ID of each necessary condition of each critical success factor, in its order.
    Changes: nothing.
    Refuses: nothing; `folder` gave a best practice whose form record.py holds, so a fault in it
    stops with its trace.
    Carries: S1 `par one for each group of necessary conditions`, each evaluator's Cut naming one.
    """
    path = os.path.join(best_practice, "best-practice.json")
    with open(path, encoding="utf-8") as f:
        factors = json.load(f)["goal"]["critical_success_factors"]
    return tuple(tuple(n["id"] for n in f["necessary_conditions"]) for f in factors)


def judged_by(run: Run, plugin_root: str, kind: str) -> tuple[Group, ...]:
    """Each group of necessary conditions that a deliverable of the kind is judged by.

    Takes: the run, rn's folder, and the deliverable's kind.
    Gives: each group of the kind's best practice, then each of the refactor one, in their order,
    so that a group's number from 0 is its place here.
    Changes: nothing.
    Refuses: fault.Wrong, as `folder` does.
    Carries: S1 `par one for each group of necessary conditions, of the kind's best practice and of
    the refactor one`, each evaluator's Cut naming one; and `T-->>O: each evaluator's Answers`,
    which names the best practice of each.
    """
    found: list[Group] = []
    for each in (kind, refactor(kind)):
        best = folder(run, plugin_root, each)
        found += [Group(each, best, ids) for ids in groups(best)]
    return tuple(found)
