"""Decides the Cut of each start of a role: which deliverable doing it takes, and which part of the
design tree, the best practices, the More kept, and the Place it starts with, in the form of the
role's in-schema, so that it reads no decision that's not its own."""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from fault import Wrong

from tree import branch, design, practices, records, rounds, turn
from tree.design import DesignTree, read
from tree.runs import Run

# rn's folder, whose own best practices a Cut names where the run has none of a kind.
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ROLES = ("tree-keeper", "generator", "evaluator")


@dataclass(frozen=True)
class Cut:
    """What one start of a role takes: the role, its run values, which the guard holds it to, its
    record's path among them, and the part of the design tree that it reads, in the form of
    `<role>-in.schema.json`."""

    role: str
    values: Mapping[str, str]
    part: Mapping[str, object]


def next_start(
    run: Run, tree: DesignTree, role: str, running: Sequence[Mapping[str, str]]
) -> Cut | None:
    """The Cut of the next start of a role.

    Takes: the run, its design tree, the role, and the run values of each start that runs.
    Gives: for the tree-keeper, the Cut of the run's design tree, or None while a start of it runs,
    as the main conversation resumes that one with each change; for the generator, the Cut of the
    first deliverable doing that no start that runs holds and whose latest round is none, holds no
    Made yet, or keeps a More for the next round; for an evaluator, the Cut of the first group of
    necessary conditions, of the kind's best practice and then of the refactor one, of a deliverable
    doing whose latest round holds a Made, that has no Answers there and that no start that runs
    holds; each with the path of a new record from `records.new_record`, after each record that a
    start that runs took; or None where no work waits.
    Changes: nothing.
    Refuses: fault.Wrong, where the role is none of rn's.
    Carries: S1 `A->>T: gets each deliverable doing, and the Cut of the first that no start that
    runs holds, with the path of a new Record for the start (Cut)`.
    """
    if role not in _ROLES:
        raise Wrong(f"{role!r} is none of rn's roles, which are {', '.join(_ROLES)}")
    taken = [each["record"] for each in running if "record" in each]
    if role == "tree-keeper":
        if any(records.role_of(each) == role for each in taken):
            return None
        return _keeper(run, records.new_record(run, role, taken))
    due = _generator_due if role == "generator" else _evaluator_due
    for deliverable in turn.doing(tree):
        start = due(run, tree, deliverable, running)
        if start:
            return _of_start(run, tree, role, records.new_record(run, role, taken, start))
    return None


def of_record(run: Run, record: str) -> Cut:
    """The Cut that a start took, by its record.

    Takes: the run, and the start's record.
    Gives: the Cut, as the run's design tree now gives it.
    Changes: nothing.
    Refuses: fault.Wrong, where the record names no start of the run.
    Carries: S1 `GD->>R: checks its record, its result, and the deliverable`, as record.py gets the
    Cut of the role it checks from tree.py's code.
    """
    role = records.role_of(record)
    if role == "tree-keeper":
        return _keeper(run, record)
    if role not in _ROLES or not records.start_of(record):
        raise Wrong(f"{record} names no start of a role of the run")
    return _of_start(run, read(run), role, record)


def _keeper(run: Run, record: str) -> Cut:
    tree = os.path.relpath(os.path.join(run.folder, "design-tree.json"), run.worktree)
    best = practices.folder(run, _ROOT, "design-tree")
    return Cut(
        "tree-keeper", {"record": record}, {"record": record, "tree": tree, "best_practice": best}
    )


def _generator_due(
    run: Run, tree: DesignTree, deliverable: str, running: Sequence[Mapping[str, str]]
) -> str:
    """The start of the deliverable's round that a generator takes, or "" where none is due."""
    if any(v.get("deliverable") == deliverable and "made" in v for v in running):
        return ""
    number = rounds.latest(run, deliverable)
    made = number and _there(run, rounds.path_in(run, deliverable, number, "made.json"))
    if not made:
        return rounds.start_name(deliverable, number or 1)
    if rounds.kept_more(run, deliverable, number):
        return rounds.start_name(deliverable, number + 1)
    return ""


def _evaluator_due(
    run: Run, tree: DesignTree, deliverable: str, running: Sequence[Mapping[str, str]]
) -> str:
    """The start of the deliverable's round and group that an evaluator takes, or ""."""
    number = rounds.latest(run, deliverable)
    if not number or not _there(run, rounds.path_in(run, deliverable, number, "made.json")):
        return ""
    held = {v.get("answers") for v in running}
    for group in range(len(_groups(run, _node(tree, deliverable)))):
        answers = rounds.path_in(run, deliverable, number, f"answers-{group}.json")
        if answers not in held and not _there(run, answers):
            return rounds.start_name(deliverable, number, group)
    return ""


def _of_start(run: Run, tree: DesignTree, role: str, record: str) -> Cut:
    """The Cut of the start of a round that the record keeps."""
    start = rounds.start_of(records.start_of(record))
    node = _node(tree, start.deliverable)
    if role == "generator":
        return _generator(run, tree, node, start, record)
    if start.group is None:
        raise Wrong(f"{record} names no group of necessary conditions for an evaluator")
    group = start.group
    kinds, ids = _groups(run, node)[group]
    answers = rounds.path_in(run, start.deliverable, start.number, f"answers-{group}.json")
    values = {"record": record, "deliverable": start.deliverable, "answers": answers}
    part = {
        "record": record,
        "deliverable": start.deliverable,
        "name": node["name"],
        "best_practice": kinds,
        "conditions": list(ids),
        "answers": answers,
    }
    return Cut(role, values, part)


def _generator(
    run: Run, tree: DesignTree, node: Mapping[str, Any], start: rounds.Start, record: str
) -> Cut:
    """The Cut of a generator's start of a round: the deliverable's own decisions alone, each with
    its ground, and the More kept in the round before."""
    path, kind = start.deliverable, node["kind"]
    made = rounds.path_in(run, path, start.number, "made.json")
    decisions = [
        {"condition": condition["id"], "decision": _decision(run, at, decision)}
        for at, condition, decision in _decisions(tree, path)
    ]
    more = rounds.kept_more(run, path, start.number - 1) if start.number > 1 else ()
    cut = {
        "goal": design.goal(tree),
        "name": node["name"],
        "inputs": list(node["inputs"]),
        "decisions": decisions,
        "more": [{"condition": m.condition, "good_when": m.good_when} for m in more],
    }
    part = {
        "record": record,
        "deliverable": path,
        "kind": kind,
        "best_practice": practices.folder(run, _ROOT, kind),
        "refactor": practices.folder(run, _ROOT, practices.refactor(kind)),
        "made": made,
        "cut": cut,
    }
    return Cut("generator", {"record": record, "deliverable": path, "made": made}, part)


def _decision(run: Run, path: str, decision: Mapping[str, Any]) -> dict[str, str]:
    """A decision as a Cut carries it, with its ground from git."""
    return {
        "path": path,
        "point": decision["about"],
        "decided": decision["decided"],
        "ground": branch.ground(run, path),
    }


def _decisions(tree: DesignTree, deliverable: str) -> list[tuple[str, Any, Any]]:
    """The path, necessary condition, and decision of each decision of the deliverable."""
    each = design.deliverables(tree)
    number = [d["path"] for d in each].index(deliverable)
    return [
        (f"deliverables/{number}/necessary_conditions/{n}/decisions/{k}", condition, decision)
        for n, condition in enumerate(each[number].get("necessary_conditions", []))
        for k, decision in enumerate(condition["decisions"])
    ]


def _groups(run: Run, node: Mapping[str, Any]) -> list[tuple[str, tuple[str, ...]]]:
    """Each group of necessary conditions that the deliverable is judged by, of its kind's best
    practice and then of the refactor one, each with the folder of its best practice."""
    found = []
    for kind in (node["kind"], practices.refactor(node["kind"])):
        best = practices.folder(run, _ROOT, kind)
        found += [(best, ids) for ids in practices.groups(best)]
    return found


def _node(tree: DesignTree, deliverable: str) -> Mapping[str, Any]:
    """The deliverable of the tree at the path."""
    for each in design.deliverables(tree):
        if each["path"] == deliverable:
            return each
    raise Wrong(f"{deliverable} is no deliverable of the design tree")


def _there(run: Run, path: str) -> bool:
    return os.path.exists(os.path.join(run.worktree, path))
