"""What a design tree is and when it holds: its file read into the form the checks take, or
refused with why; each way it fails to hold, as pin's architecture names them, its problems; and
the open decisions that can be decided now, each it builds on being decided."""

from __future__ import annotations

import json
from typing import Any

# Who settles a decision: the person, a fact found and confirmed, what follows from the goal and the
# decisions before it, or the maker AI that handed the tree over, whose points the pinner keeps.
SETTLED_BY = ("user", "research", "reasoning", "maker")
# The tree's form, said once for each message that names a part of it.
TREE = "the tree must be an object with goal, questions and decisions"
TEXT = "must be a text that is not empty"
TEXTS = "must be a list of texts"
IDS = "must be a list of IDs"


class Unreadable(Exception):
    """The tree cannot be checked: its file is missing, is not JSON or is out of form. The message
    says why, a line for each fault."""


def load(path: str) -> dict[str, Any]:
    """The design tree in the file at the path, as written, keys of a caller's own among it;
    refuses, by Unreadable, a file that is missing, is not JSON or is out of the tree's form."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise Unreadable(f"there is no file {path}") from None
    except json.JSONDecodeError as e:
        raise Unreadable(f"it is not JSON: {e.msg} at line {e.lineno} column {e.colno}") from None
    faults = form_faults(data)
    if faults:
        raise Unreadable("\n".join(faults))
    return data


def is_text(value: Any) -> bool:
    """Whether the value is a text that is not empty."""
    return isinstance(value, str) and bool(value)


def is_texts(value: Any) -> bool:
    """Whether the value is a list of texts, each not empty."""
    return isinstance(value, list) and all(is_text(v) for v in value)


def form_faults(data: Any) -> list[str]:
    """Each way the data is out of the tree's form, in the order of its parts; none where it is in
    form, so the checks of problems can read it."""
    if not isinstance(data, dict):
        return [TREE]
    faults = goal_faults(data.get("goal"))
    questions, decisions = data.get("questions"), data.get("decisions")
    if not isinstance(questions, list):
        faults.append("questions must be a list")
        questions = []
    for n, q in enumerate(questions):
        faults += question_faults(n, q)
    if not isinstance(decisions, list):
        faults.append("decisions must be a list")
        decisions = []
    for n, d in enumerate(decisions):
        faults += decision_faults(n, d)
    return faults or id_faults(questions, decisions)


def goal_faults(goal: Any) -> list[str]:
    """Each way the goal is out of form."""
    if not isinstance(goal, dict):
        return ["goal must be an object with what and grounds"]
    faults = [] if is_text(goal.get("what")) else [f"goal.what {TEXT}"]
    return faults + ([] if is_texts(goal.get("grounds")) else [f"goal.grounds {TEXTS}"])


def question_faults(n: int, question: Any) -> list[str]:
    """Each way the question at the place n of the questions is out of form."""
    if not isinstance(question, dict):
        return [f"questions[{n}] must be an object with id and what"]
    faults = [] if is_text(question.get("id")) else [f"questions[{n}].id must be a text"]
    return faults + ([] if is_text(question.get("what")) else [f"questions[{n}].what {TEXT}"])


def decision_faults(n: int, decision: Any) -> list[str]:
    """Each way the decision at the place n of the decisions is out of form."""
    at = f"decisions[{n}]"
    if not isinstance(decision, dict):
        return [f"{at} must be an object"]
    checks = [
        ("id", is_text, TEXT),
        ("what", is_text, TEXT),
        ("contributes_to", is_texts, IDS),
        ("builds_on", is_texts, IDS),
        ("decided", lambda v: v is None or is_text(v), f"{TEXT}, or null"),
        (
            "settled_by",
            lambda v: v is None or v in SETTLED_BY,
            "must be user, research, reasoning or maker, or null",
        ),
        ("grounds", is_texts, TEXTS),
    ]
    return [f"{at}.{key} {rule}" for key, ok, rule in checks if not ok(decision.get(key))]


def id_faults(questions: list[dict[str, Any]], decisions: list[dict[str, Any]]) -> list[str]:
    """Each ID used twice, and each ID a decision names that the tree does not hold where it is
    named, or that is the decision's own."""
    ids = [q["id"] for q in questions] + [d["id"] for d in decisions]
    seen: set[str] = set()
    twice: set[str] = set()
    for i in ids:
        (twice if i in seen else seen).add(i)
    faults = [f"the ID {i} is used twice" for i in sorted(twice)]
    decided_ids = {d["id"] for d in decisions}
    for d in decisions:
        for i in d["contributes_to"]:
            if i == d["id"]:
                faults.append(f"{i} contributes to itself")
            elif i not in ids:
                faults.append(f"{d['id']} contributes to {i}, which is not in the tree")
        for i in d["builds_on"]:
            if i == d["id"]:
                faults.append(f"{i} builds on itself")
            elif i not in decided_ids:
                faults.append(f"{d['id']} builds on {i}, which is not a decision of the tree")
    return faults


def problems(tree: dict[str, Any]) -> list[str]:
    """Each way a tree in form fails to hold, a sentence each, in the order of the checks: a goal or
    a question nothing serves; a decision that reaches no question; decisions out of the order
    builds_on gives; and a decision settled with what it rests on missing. None where it holds."""
    return gaps(tree) + unreached(tree) + out_of_order(tree) + unsettled(tree)


def gaps(tree: dict[str, Any]) -> list[str]:
    """The goal with no question under it, and each question no decision contributes to."""
    if not tree["questions"]:
        return ["The goal has no question that must hold for it."]
    served = {i for d in tree["decisions"] for i in d["contributes_to"]}
    return [
        f"{q['id']} is served by no decision." for q in tree["questions"] if q["id"] not in served
    ]


def unreached(tree: dict[str, Any]) -> list[str]:
    """Each decision from which no chain of contributes_to reaches a question."""
    questions = {q["id"] for q in tree["questions"]}
    serves = {d["id"]: d["contributes_to"] for d in tree["decisions"]}
    found = []
    for d in tree["decisions"]:
        seen, left = set(), list(d["contributes_to"])
        while left and not questions & set(left):
            seen.update(left)
            left = [i for j in left for i in serves[j] if i not in seen]
        if not left:
            found.append(f"{d['id']} reaches no question, so it serves nothing.")
    return found


def out_of_order(tree: dict[str, Any]) -> list[str]:
    """Each loop of builds_on, named once from its first decision in the tree, and each decision
    decided while one it builds on is open."""
    by_id = {d["id"]: d for d in tree["decisions"]}
    found, looped = [], set()
    for d in tree["decisions"]:
        loop = loop_from(d["id"], by_id)
        if loop and not looped & set(loop):
            looped.update(loop)
            found.append(
                f"{listed(loop)} build on one another in a loop, so none can be decided first."
            )
    for d in tree["decisions"]:
        for i in d["builds_on"]:
            if d["decided"] is not None and by_id[i]["decided"] is None:
                found.append(
                    f"{d['id']} is decided before {i}, which it builds on and which is still open."
                )
    return found


def loop_from(start: str, by_id: dict[str, dict[str, Any]]) -> list[str]:
    """The decisions of the shortest loop of builds_on that leads from start back to it, in the
    order the chain meets them, start first; none where no chain from start comes back to it. The
    chains are followed breadth first, so the first to come back is the shortest."""
    paths = [[start]]
    seen = {start}
    while paths:
        path = paths.pop(0)
        for i in by_id[path[-1]]["builds_on"]:
            if i == start:
                return path
            if i not in seen:
                seen.add(i)
                paths.append(path + [i])
    return []


def listed(ids: list[str]) -> str:
    """The IDs in words, as "D1, D2 and D3"."""
    return ", ".join(ids[:-1]) + " and " + ids[-1]


def unsettled(tree: dict[str, Any]) -> list[str]:
    """Each decision whose decided, settled_by and grounds do not go together: a decision decided
    by no one named, named as settled while not decided, or decided on no ground."""
    found = []
    for d in tree["decisions"]:
        if d["decided"] is not None and d["settled_by"] is None:
            found.append(f"{d['id']} is decided, but not by whom or what: give its settled_by.")
        elif d["decided"] is None and d["settled_by"] is not None:
            found.append(f"{d['id']} has a settled_by, but is not decided: give what was decided.")
        elif d["decided"] is not None and not d["grounds"]:
            found.append(f"{d['id']} is decided on no ground: give what it rests on.")
    return found


def ready(tree: dict[str, Any]) -> list[str]:
    """The IDs of the open decisions each of whose builds_on is decided, in the order the tree
    lists them: those that can be decided now."""
    decided = {d["id"] for d in tree["decisions"] if d["decided"] is not None}
    return [
        d["id"]
        for d in tree["decisions"]
        if d["decided"] is None and set(d["builds_on"]) <= decided
    ]
