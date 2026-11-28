"""Decides what each change makes of the work's steering: the orchestrator's aim taken in, the tree
whole and the way to the target, each step and deliverable that the steering already holds keeping
its status and where it is on its way, unless the aim says what it takes next; each deliverable
moved on by the result of its next role, where nothing is to weigh; a step marked as the work moves
on; and the inspection's pass."""

from __future__ import annotations

import copy
from typing import Any

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
    the same words keeping its status, and each of its deliverables at the same path keeping its
    own and where it is on its way, every other step and deliverable open; each deliverable whose
    next the aim says taking it with no entry, as its next role starts its own: generator and
    the judged Rounds kept, anew as generator from its first Round, fixer, refactorer, or done,
    and its step open again where it opens; and the inspection passed where the steering holds it
    so and the aim adds no step, as a step added grows the pull request.
    Changes: nothing.
    Refuses: Wrong where it would make a deliverable again past LIMIT judged Rounds, as the user
    confirms what they leave, naming it.
    """
    state = steering["state"] if steering else {"issues": _NO_ISSUES, "steps": []}
    steps = state["steps"]
    if "steps" in aim:
        steps = [_kept(each, state["steps"]) for each in aim["steps"]]
    issues = copy.deepcopy(aim.get("issues", state["issues"]))
    held = [(each["for"], each["settles"]) for each in state["steps"]]
    added = any((each["for"], each["settles"]) not in held for each in steps)
    inspected = {"inspected": True} if state.get("inspected") and not added else {}
    return {
        "ost": copy.deepcopy(aim["ost"]),
        "state": {"issues": issues, "steps": steps, **inspected},
    }


def _kept(step: dict[str, Any], held: list[dict[str, Any]]) -> dict[str, Any]:
    same = next(
        (each for each in held if (each["for"], each["settles"]) == (step["for"], step["settles"])),
        None,
    )
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
    if "refactor" in told:
        kept["refactor"] = told["refactor"]
    if had:
        kept.update({key: had[key] for key in ("status", *_WAY) if key in had})
    said = told.get("next")
    if said is None:
        return kept
    for key in ("next", "entry"):
        kept.pop(key, None)
    if said == "done":
        return {**kept, "status": "done"}
    if said == "generator" and kept.get("judged", 0) >= LIMIT:
        raise Wrong(
            f"{told['path']} has had its {LIMIT} judged Rounds; ask the user whether to mend what"
            " they left, then say fixer or done"
        )
    if said == "anew":
        kept.pop("judged", None)
        said = "generator"
    return {**kept, "status": "open", "next": said}


def step_marked(steering: Steering, number: int, status: str) -> Steering:
    """The steering with a step marked.

    Takes: the steering, the step's number from 1 in the order of its steps, and its new status.
    Gives: a new steering with the step at that status.
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
    return marked


def moved(steering: Steering, results: dict[str, dict[str, dict[str, Any]]]) -> Steering:
    """The steering with each deliverable moved on by the result of its next role.

    Takes: the steering, and for each open deliverable's path, the results that its entry holds,
    by role.
    Gives: a new steering in which each open deliverable whose next role's result is there takes
    what follows it: a generator's made, its evaluator; a point, a generator's or a refactorer's,
    the orchestrator's weighing; an evaluator's result, one more judged Round, then its weighing of
    what it found, else what follows a deliverable made; a fixer's, what follows a deliverable
    made; a refactorer's made, its end. What follows a deliverable made is its refactorer, where
    the steering gives it a `refactor`, else its end. Each other deliverable stays as it is.
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
    """Takes a deliverable made on to its refactoring, where the steering gives it one, else to its
    end."""
    if "refactor" in each:
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
