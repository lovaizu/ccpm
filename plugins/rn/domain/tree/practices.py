"""Decides where the best practice of each kind lies for a run, the one made on a run, in
`.rn/best-practices/<kind>/` of the run's worktree, over rn's own of that kind, and which refactor
best practice and which groups of necessary conditions it gives a deliverable."""

from __future__ import annotations

import json
import os

from fault import CantRun, Wrong

from tree.runs import Run


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
    Refuses: fault.CantRun, where its best-practice.json can't be read or leaves its form, as rn
    or the run's own best practice made it.
    Carries: S1 `par one for each group of necessary conditions`, each evaluator's Cut naming one.
    """
    path = os.path.join(best_practice, "best-practice.json")
    try:
        with open(path, encoding="utf-8") as f:
            factors = json.load(f)["goal"]["critical_success_factors"]
        return tuple(tuple(n["id"] for n in f["necessary_conditions"]) for f in factors)
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise CantRun(f"the groups of {path} can't be read: {e!r}") from None
