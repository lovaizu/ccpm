"""Decides the course of the Rounds: which starts are due, each deliverable's beside those of the
others being made, whether a Round makes the content by the kind's best practice or refactors it by
the refactor best practice, the limit of two Rounds of each, and the groups a later Round judges,
those holding a condition whose decisions changed."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from tree.design import Tree
from tree.rounds import Start

# rn's own best practices, beside its code.
_PRACTICES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "best-practices")
# The most Rounds of content, and of refactoring, before each finding left goes to the user.
_LIMIT = 2


@dataclass(frozen=True)
class Due:
    """A start due: the deliverable's path, its role, the group an evaluator judges or "" for the
    generator, the best practice its Round works by, and the Round's number."""

    deliverable: str
    role: str
    group: str
    best_practice: str
    round: int


def groups(best_practice: str) -> Mapping[str, Sequence[str]]:
    """Each group of the best practice's necessary conditions, by its ID, with the ID of each
    condition it bundles, in the best practice's order.

    Takes: the folder name of one of rn's best practices, such as code.
    Gives: the groups, such as {"C1": ["N1", "N2"]}.
    Refuses: OSError where rn has no such best practice, as the Cut that names it is at fault."""
    with open(os.path.join(_PRACTICES, best_practice, "best-practice.json"), encoding="utf-8") as f:
        factors = json.load(f)["goal"]["critical_success_factors"]
    return {c["id"]: [n["id"] for n in c["necessary_conditions"]] for c in factors}


def due(tree: Tree, starts: Sequence[Start], running: Sequence[Due]) -> Sequence[Due]:
    """Each start due, beside those that run.

    Takes: the design tree, each start of the run's Rounds, and each start that runs. A start with
    no result counts for nothing, as one that didn't end, but for the number of the next Round.
    Gives: for each item of `work` that makes a deliverable with no earlier item that names it or
    one of its inputs, beside each other such item, the generator, where its
    latest Round has no result of the generator, its point's answer changed a decision, or its
    evaluators judged it short on a condition that the design tree doesn't hold good and a decision
    changed since, within the limit of two Rounds of content and two of refactoring that only the
    user's decision passes; or one evaluator for each group due once the generator made it; or
    none, such as while a point waits, or once the limit leaves each finding to the orchestrator,
    which puts it to the user as a proposal. Each new Round takes the next number of the run.
    Refuses: nothing."""
    busy = {(r.role, r.deliverable, r.group) for r in running}
    ended = [s for s in starts if s.result is not None]
    wanted = _wanted(tree, ended, _last(starts) + 1)
    return [d for d in wanted if (d.role, d.deliverable, d.group) not in busy]


def _wanted(tree: Tree, starts: Sequence[Start], next_: int) -> list[Due]:
    """Each start that the course wants next, before those that run are left out: of each
    deliverable that can be made now, each new Round numbered from `next_`, after the new ones
    before it."""
    nodes = {d["path"]: d for d in tree["deliverables"]}
    wanted: list[Due] = []
    for path in _ready(tree, nodes):
        due = _of(tree, nodes[path], starts, next_)
        next_ += any(d.round == next_ for d in due)
        wanted += due
    return wanted


def _ready(tree: Tree, nodes: Mapping[str, Mapping[str, Any]]) -> list[str]:
    """The path of each deliverable that `work` makes and that can be made now: no earlier item of
    `work` names it, as a point of it, or one of its inputs, as one still being made, since
    work.faults holds each item after each input that isn't done."""
    ready: list[str] = []
    before: set[str] = set()
    for item in tree["work"]:
        path = item["path"]
        waits = before & {path, *nodes[path].get("inputs", [])}
        if item["do"] == "make" and not waits:
            ready.append(path)
        before.add(path)
    return ready


def _of(tree: Tree, node: Mapping[str, Any], starts: Sequence[Start], next_: int) -> list[Due]:
    """Each start that the course wants next of the deliverable, from the starts that ended, each
    with its result, a new Round numbered `next_`."""
    path = node["path"]
    mine = [s for s in starts if s.cut["deliverable"]["path"] == path]
    if not mine:
        return [Due(path, "generator", "", node["kind"], next_)]
    made = [s for s in mine if s.role == "generator"]
    latest = made[-1]
    practice = latest.cut["best_practice"]
    result: Any = latest.result
    if result["result"] != "made":
        again = _changed(latest.cut["decisions"], decisions(tree, path))
        return [Due(path, "generator", "", practice, next_)] if again else []
    judged = [s for s in mine if s.round == latest.round and s.role == "evaluator"]
    pending = _pending(node, made, judged)
    if pending is not None:
        return [Due(path, "evaluator", g, practice, latest.round) for g in pending]
    return _after(tree, node, made, judged, next_)


def _last(starts: Sequence[Start]) -> int:
    """The number of the run's latest Round, or 0 before the first."""
    return max((s.round for s in starts), default=0)


def _made(made: Sequence[Start], practice: str) -> list[Start]:
    """Each generator's start by the best practice that made the deliverable, a point none."""
    return [
        s
        for s in made
        if s.cut["best_practice"] == practice and s.result and s.result["result"] == "made"
    ]


def _pending(node: Mapping[str, Any], made: Sequence[Start], judged: Sequence[Start]) -> Any:
    """Each group of the latest Round that hasn't answered, or None once each has.
    A later Round of the deliverable's own kind judges only the groups of the conditions whose
    decisions changed, or each group where an input's decision changed."""
    latest = made[-1]
    practice = latest.cut["best_practice"]
    wanted = groups(practice)
    earlier = _made(made[:-1], practice)
    if earlier and practice == node["kind"]:
        changed = _changed(earlier[-1].cut["decisions"], latest.cut["decisions"])
        if all(each == node["path"] for each, _ in changed):
            own = {condition for _, condition in changed}
            wanted = {g: c for g, c in wanted.items() if set(c) & own}
    answered = {s.group for s in judged if s.result is not None}
    return [g for g in wanted if g not in answered] or None


def _changed(
    before: Sequence[Mapping[str, Any]], after: Sequence[Mapping[str, Any]]
) -> set[tuple[str, str]]:
    """Each condition, by its node's path and its ID, whose decisions differ between two Cuts."""
    return {(each[0], each[1]) for each in _held(before) ^ _held(after)}


def _held(decisions: Sequence[Mapping[str, Any]]) -> set[tuple[str, str, str, Any, Any]]:
    """Each decision by its node's path, its condition, its point, what it holds, and who, or None
    for a point still open, which the design tree holds with no `by`."""
    return {(d["path"], d["condition"], d["about"], d["decided"], d.get("by")) for d in decisions}


def _by_user(before: Sequence[Mapping[str, Any]], after: Sequence[Mapping[str, Any]]) -> bool:
    """Whether a decision by the user holds since the earlier Cut that it didn't hold then."""
    return any(each[4] == "user" for each in _held(after) - _held(before))


def _after(
    tree: Tree, node: Mapping[str, Any], made: Sequence[Start], judged: Sequence[Start], next_: int
) -> list[Due]:
    """The generator due once each evaluator of the latest Round answered, or none. A condition
    short counts as good where the design tree holds it good, as the orchestrator found that its
    people would never meet it."""
    path = node["path"]
    practice = made[-1].cut["best_practice"]
    good = {c["id"] for c in node.get("necessary_conditions", []) if c["good"]}
    short = {m["condition"] for s in judged if s.result for m in s.result["more"]}
    if practice == node["kind"]:
        short -= good
    if not short:
        if practice != node["kind"]:
            return []
        refactor = "refactor-doc" if path.endswith(".md") else "refactor-code"
        return [Due(path, "generator", "", refactor, next_)]
    rounds = _made(made, practice)
    now = decisions(tree, path)
    if not _changed(rounds[-1].cut["decisions"], now):
        return []
    if len(rounds) >= _LIMIT and not _by_user(rounds[-1].cut["decisions"], now):
        return []
    return [Due(path, "generator", "", practice, next_)]


def decisions(tree: Tree, path: str) -> list[dict[str, Any]]:
    """Each decision that the generator of a deliverable works from.

    Takes: the design tree, and the deliverable's path.
    Gives: each decision of its node, then of each input node that keeps its conditions, as a node
    with no file does, in the order of the deliverable's `inputs`, each by its node's path and its
    condition, in the order its node holds them.
    Refuses: nothing."""
    nodes = {d["path"]: d for d in tree["deliverables"]}
    held = [path, *(i for i in nodes[path].get("inputs", []) if i in nodes)]
    return [
        {"path": each, "condition": c["id"], **d}
        for each in held
        for c in nodes[each].get("necessary_conditions", [])
        for d in c["decisions"]
    ]
