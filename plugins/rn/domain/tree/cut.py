"""Decides the Cut of each start of a role: which deliverable doing it takes, and which part of the
design tree, the best practices, the More kept, and the Place it starts with, in the form of the
role's in-schema, so that it reads no decision that's not its own."""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, cast

from fault import Wrong

from tree import branch, course, design, place, practices, records, rounds, turn
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
    first deliverable doing, in the work's order, with a file, that no start that runs holds and
    whose round `course.next_round` gives, naming the best practice that the round works by, with
    the commit at which the deliverable was last done, from `branch.done_at`, where it was done
    before; for an evaluator, the Cut of the first group that `course.rounds_of` gives the latest
    round of such a deliverable to judge, where it holds a Made, that has no Answers there and that
    no start that runs holds; each with the path of a new record from
    `records.new_record`, after each record that a start that runs took, and, where a start of the
    same round and group stood at a step, the step of the latest one's Place, from
    `rounds.stood_place` and `place.read`, in the generator's `cut` or beside the evaluator's
    conditions; or None where no work waits.
    Changes: nothing.
    Refuses: fault.Wrong, where the role is none of rn's or that Place leaves its form;
    fault.CantRun, where that Place can't be read.
    Carries: S1 `A->>T: gets each deliverable doing, and the Cut of the first in the work's order
    that no start that runs holds, with the path of a new Record for the start (Cut)`; S5
    `O->>G: starts each that stood in a step, at that step (Cut, Place)`, and the same of each
    evaluator.
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
        # A node with no file gets no round, as the orchestrator settles its decisions.
        if design.deliverable(tree, deliverable).get("file") is False:
            continue
        start = due(run, tree, deliverable, running)
        if start:
            found = _of_start(run, tree, role, records.new_record(run, role, taken, start))
            return _at_place(run, found, start)
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
    due = course.next_round(run, _ROOT, tree, deliverable)
    return rounds.start_name(deliverable, due.number) if due else ""


def _evaluator_due(
    run: Run, tree: DesignTree, deliverable: str, running: Sequence[Mapping[str, str]]
) -> str:
    """The start of the deliverable's round and group that an evaluator takes, or ""."""
    each = course.rounds_of(run, _ROOT, tree, deliverable)
    if not each or not _there(run, rounds.path_in(run, deliverable, each[-1].number, "made.json")):
        return ""
    held = {v.get("answers") for v in running}
    for group in each[-1].groups:
        answers = rounds.path_in(run, deliverable, each[-1].number, f"answers-{group}.json")
        if answers not in held and not _there(run, answers):
            return rounds.start_name(deliverable, each[-1].number, group)
    return ""


def _of_start(run: Run, tree: DesignTree, role: str, record: str) -> Cut:
    """The Cut of the start of a round that the record keeps."""
    start = rounds.start_of(records.start_of(record))
    node = design.deliverable(tree, start.deliverable)
    if role == "generator":
        return _generator(run, tree, node, start, record)
    if start.group is None:
        raise Wrong(f"{record} names no group of necessary conditions for an evaluator")
    group = start.group
    judged = practices.judged_by(run, _ROOT, node["kind"])[group]
    kinds, ids = judged.folder, judged.conditions
    answers = rounds.path_in(run, start.deliverable, start.number, f"answers-{group}.json")
    values = {"record": record, "deliverable": start.deliverable, "answers": answers}
    part = {
        "record": record,
        "deliverable": start.deliverable,
        "goal": design.goal(tree),
        "name": node["name"],
        "best_practice": kinds,
        "conditions": list(ids),
        "answers": answers,
    }
    return Cut(role, values, part)


def _at_place(run: Run, found: Cut, start: str) -> Cut:
    """The Cut of a start anew of a round, with the step that the latest start of that round
    stood at, by its Place, where one stood: in the generator's cut, or beside an evaluator's
    conditions."""
    path = rounds.stood_place(run, start)
    if path is None:
        return found
    step = place.read(path).step
    if found.role == "generator":
        part = dict(found.part, cut=dict(cast(Any, found.part)["cut"], step=step))
    else:
        part = dict(found.part, step=step)
    return Cut(found.role, found.values, part)


def _generator(
    run: Run, tree: DesignTree, node: Mapping[str, Any], start: rounds.Start, record: str
) -> Cut:
    """The Cut of a generator's start of a round: its inputs, the decisions of each input node with
    no file, the commit at which the deliverable
    was last done where it was done before, the deliverable's own decisions alone, each with its
    ground, and the More kept in the round before."""
    path, kind = start.deliverable, node["kind"]
    structure = course.of_structure(run, _ROOT, tree, path, start.number)
    works_by = practices.refactor(kind) if structure else kind
    made = rounds.path_in(run, path, start.number, "made.json")
    decisions = [
        {"condition": condition["id"], "decision": _decision(run, at, decision)}
        for at, condition, decision in _decisions(tree, path)
    ]
    more = rounds.kept_more(run, path, start.number - 1) if start.number > 1 else ()
    done_at = branch.done_at(run, path)
    cut = {
        "goal": design.goal(tree),
        "name": node["name"],
        "inputs": list(node["inputs"]),
        "nodes": _nodes_taken(tree, node["inputs"]),
        **({"done_at": done_at} if done_at else {}),
        "decisions": decisions,
        "more": [
            {
                "best_practice": m.best_practice,
                "condition": m.condition,
                "decision": m.decision,
                "good_when": m.good_when,
            }
            for m in more
        ],
    }
    part = {
        "record": record,
        "deliverable": path,
        "kind": kind,
        "best_practice": practices.folder(run, _ROOT, works_by),
        "made": made,
        "cut": cut,
    }
    return Cut("generator", {"record": record, "deliverable": path, "made": made}, part)


def _nodes_taken(tree: DesignTree, inputs: Sequence[str]) -> list[dict[str, Any]]:
    """Each input that is a node with no file, with its kind and the decisions that hold what its
    file would, as the deliverable built on it reads them there."""
    found = []
    for each in design.deliverables(tree):
        if each["path"] in inputs and each.get("file") is False:
            decisions = [
                {"condition": c["id"], "point": d["about"], "decided": d["decided"]}
                for c in each.get("necessary_conditions", [])
                for d in c["decisions"]
            ]
            found.append({"path": each["path"], "kind": each["kind"], "decisions": decisions})
    return found


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


def _there(run: Run, path: str) -> bool:
    return os.path.exists(os.path.join(run.worktree, path))
