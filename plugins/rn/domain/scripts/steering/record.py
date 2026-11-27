"""Decides what each change makes of the work's steering: the orchestrator's aim taken in, the tree
whole and the way to the target, each step and deliverable that the steering already holds keeping
its status and where it is on its way, unless the aim says what it takes next; each deliverable
moved on by the result of its next role, where nothing is to weigh; a step marked as the work moves
on; and the inspection's pass."""

from __future__ import annotations

import copy
from typing import Any

import practice
from fault import Wrong

# A steering, and the orchestrator's aim, as `json.load` gives them, each in its schema's form.
Steering = dict[str, Any]
# Each status of a step, as the steering's schema names them.
STEP = ("open", "trying", "done")
# How many judged Rounds of content a deliverable takes at most, as remaking that brings no remedy
# has a limit (the architecture's P3.3). What they leave goes to the user, with no exception for a
# decision made since, so that no Round records how many decisions the work held.
LIMIT = 2
# What a deliverable keeps of where it is on its way, as the steering's schema names it.
_WAY = ("next", "judged", "entry")
# The work's issues while no aim has named them yet.
_NO_ISSUES: dict[str, list[int]] = {"closes": [], "refs": []}


def taken_in(steering: Steering | None, aim: dict[str, Any]) -> Steering:
    """The steering with the orchestrator's aim taken in.

    Takes: the steering as it stands, or None where the work has none yet, and the aim
    in its schema's form.
    Gives: a new steering: the aim's tree whole; its issues, else the steering's, else none;
    and its steps, else the steering's, each step that the steering holds for the same need with
    the same words, else at the same place for the same need, keeping its status, and each of its
    deliverables at the same path keeping its own and where it is on its way, every other step
    and deliverable open; each deliverable whose
    next the aim says taking it with no entry, as its next role starts its own: generator and
    the judged Rounds kept, anew as generator from its first Round, fixer, refactorer, or done,
    and its step open again where it opens; and the inspection passed where the steering holds it
    so and the aim adds no step, as a step added grows the pull request.
    Changes: nothing.
    Refuses: Wrong where it would drop or change a decision by the user, as only they change it;
    where its target or a step's need names no opportunity of its tree; where it would make a
    deliverable again past LIMIT judged Rounds, as the user confirms what they leave; where it
    would mend one by a fixer before its Rounds are over and it isn't done, as a Fix mends only
    what the Rounds left or what was tried; or where it would leave one waiting on a weighing with
    no question asked; naming each.
    """
    state = steering["state"] if steering else {"issues": _NO_ISSUES, "steps": []}
    _decisions_kept(steering["ost"]["decisions"] if steering else [], aim["ost"]["decisions"])
    _named(aim)
    steps = state["steps"]
    added = False
    if "steps" in aim:
        found = [_same(each, place, state["steps"]) for place, each in enumerate(aim["steps"])]
        steps = [_kept(each, same) for each, same in zip(aim["steps"], found)]
        added = None in found
    _settled(steps, aim["ost"]["questions"])
    issues = copy.deepcopy(aim.get("issues", state["issues"]))
    inspected = {"inspected": True} if state.get("inspected") and not added else {}
    return {
        "ost": copy.deepcopy(aim["ost"]),
        "state": {"issues": issues, "steps": steps, **inspected},
    }


def _decisions_kept(held: list[dict[str, Any]], told: list[dict[str, Any]]) -> None:
    """Refuses an aim that drops or changes a decision by the user."""
    for each in held:
        if each["by"] == "user" and each not in told:
            raise Wrong(
                f"the aim drops or changes the user's decision {each['decision']!r}; keep it word"
                " for word, as only the user changes it"
            )


def _named(aim: dict[str, Any]) -> None:
    """Refuses a target or a step's need that names no opportunity of the aim's tree."""
    ids, stack = set(), list(aim["ost"]["opportunities"])
    while stack:
        each = stack.pop()
        ids.add(each["id"])
        stack += each["opportunities"]
    target = aim["ost"]["target"]
    named = ([target] if target is not None else []) + [s["for"] for s in aim.get("steps", [])]
    for each in named:
        if each not in ids:
            raise Wrong(f"{each} names no opportunity of the tree; give one of its ids")


def _same(step: dict[str, Any], place: int, held: list[dict[str, Any]]) -> dict[str, Any] | None:
    """The step that the steering holds for the same need with the same words, else the one at
    the same place for the same need, as a step reworded is still the same step."""
    for each in held:
        if (each["for"], each["settles"]) == (step["for"], step["settles"]):
            return each
    if place < len(held) and held[place]["for"] == step["for"]:
        return held[place]
    return None


def _kept(step: dict[str, Any], same: dict[str, Any] | None) -> dict[str, Any]:
    had = {each["path"]: each for each in same["deliverables"]} if same else {}
    deliverables = [_deliverable(each, had.get(each["path"])) for each in step["deliverables"]]
    status = same["status"] if same else "open"
    reopened = any(each["status"] == "open" for each in deliverables) and status != "open"
    return {
        "for": step["for"],
        "settles": step["settles"],
        "deliverables": deliverables,
        "status": "open" if reopened and _told(step) else status,
    }


def _told(step: dict[str, Any]) -> bool:
    """Whether the aim says what a deliverable of the step takes next, other than its end."""
    return any(each.get("next", "done") != "done" for each in step["deliverables"])


def _deliverable(told: dict[str, Any], had: dict[str, Any] | None) -> dict[str, Any]:
    """The deliverable as the aim names it, keeping what the steering holds of it, and taking
    what the aim says it takes next."""
    kept: dict[str, Any] = {"path": told["path"], "kind": told["kind"], "status": "open"}
    if had:
        kept.update({key: had[key] for key in ("status", *_WAY) if key in had})
    said = told.get("next")
    if said is None:
        return kept
    for key in ("next", "entry"):
        kept.pop(key, None)
    if said == "done":
        return {**kept, "status": "done"}
    if said == "fixer" and kept["status"] != "done" and kept.get("judged", 0) < LIMIT:
        raise Wrong(
            f"{told['path']} isn't through its Rounds; make it again by its generator, as a Fix"
            " mends only what the Rounds left or what was tried"
        )
    if said == "generator" and kept.get("judged", 0) >= LIMIT:
        raise Wrong(
            f"{told['path']} has had its {LIMIT} judged Rounds; ask the user whether to mend what"
            " they left, then say fixer or done"
        )
    if said == "anew":
        kept.pop("judged", None)
        said = "generator"
    return {**kept, "status": "open", "next": said}


def _settled(steps: list[dict[str, Any]], questions: list[str]) -> None:
    """Refuses a weighing that leaves a deliverable waiting on it with no question asked."""
    if questions:
        return
    for step in steps:
        for each in step["deliverables"]:
            if each["status"] == "open" and each.get("next") == "weigh":
                raise Wrong(
                    f"{each['path']} waits on this weighing; say what it takes next, or ask the"
                    " user"
                )


def step_marked(steering: Steering, number: int, status: str) -> tuple[Steering, str]:
    """The steering with a step marked.

    Takes: the steering, the step's number from 1 in the order of its steps, and its new status.
    Gives: a new steering with the step at that status, and the step's words.
    Changes: nothing.
    Refuses: Wrong where no step has the number, where the status is none of the step's, or where
    the step would be trying with a deliverable not done, as the user tries only what's made.
    """
    steps = steering["state"]["steps"]
    if not 1 <= number <= len(steps):
        raise Wrong(f"no step {number}; the steering holds {len(steps)}, numbered from 1")
    if status not in STEP:
        raise Wrong(f"{status!r} isn't a step's status; give one of {', '.join(STEP)}")
    step = steps[number - 1]
    left = [each["path"] for each in step["deliverables"] if each["status"] != "done"]
    if status == "trying" and left:
        raise Wrong(f"step {number} isn't made yet: {', '.join(left)} not done; make each first")
    marked = copy.deepcopy(steering)
    marked["state"]["steps"][number - 1]["status"] = status
    return marked, step["settles"]


def moved(steering: Steering, results: dict[str, dict[str, dict[str, Any]]]) -> Steering:
    """The steering with each deliverable moved on by the result of its next role.

    Takes: the steering, and for each open deliverable's path, the results that its entry holds,
    by role.
    Gives: a new steering in which each open deliverable whose next role's result is there takes
    what follows it: a generator's made, its evaluator; a point, a generator's or a refactorer's,
    the orchestrator's weighing; an evaluator's result, one more judged Round, then its weighing of
    what it found, else what follows a deliverable made; a fixer's, what follows a deliverable
    made; a refactorer's made, its end. What follows a deliverable made is its refactorer, where
    its kind is refactored, else its end. Each other deliverable stays as it is.
    Changes: nothing.
    Refuses: nothing.
    """
    marked = copy.deepcopy(steering)
    for step in marked["state"]["steps"]:
        for each in step["deliverables"]:
            role = each.get("next", "generator")
            found = results.get(each["path"], {}).get(role)
            if each["status"] == "open" and found is not None:
                _on(each, role, found)
    return marked


def _on(each: dict[str, Any], role: str, found: dict[str, Any]) -> None:
    """Moves the deliverable on by its next role's result."""
    if found["result"] == "point":
        each["next"] = "weigh"
    elif role == "generator":
        each["next"] = "evaluator"
    elif role == "evaluator":
        each["judged"] = each.get("judged", 0) + 1
        if found["more"]:
            each["next"] = "weigh"
        else:
            _made(each)
    elif role == "fixer":
        _made(each)
    else:
        _ended(each)


def _made(each: dict[str, Any]) -> None:
    """Takes a deliverable made on to its refactoring, where its kind has one, else to its end."""
    if practice.refactoring(each["kind"]):
        each["next"] = "refactorer"
        each.pop("entry", None)
    else:
        _ended(each)


def _ended(each: dict[str, Any]) -> None:
    each["status"] = "done"
    for key in ("next", "entry"):
        each.pop(key, None)


def inspected_marked(steering: Steering) -> Steering:
    """The steering with the pull request's inspection passed.

    Takes: the steering.
    Gives: a new steering that holds the inspection passed, so that it's due no more.
    Changes: nothing.
    Refuses: Wrong where a step isn't done, as the inspection comes once each is, naming the
    first.
    """
    for number, step in enumerate(steering["state"]["steps"], 1):
        if step["status"] != "done":
            raise Wrong(f"step {number} isn't done; check the pull request once each step is done")
    marked = copy.deepcopy(steering)
    marked["state"]["inspected"] = True
    return marked
