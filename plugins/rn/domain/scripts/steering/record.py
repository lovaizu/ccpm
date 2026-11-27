"""Decides what each change makes of a run's steering: the pruner's result taken in, the tree
whole and the way to the target, each step and deliverable that the steering already holds keeping
its status; a step or a deliverable marked as the run moves on; and the inspection's pass."""

from __future__ import annotations

import copy
from typing import Any

from fault import Wrong

# A steering, and the pruner's result, as `json.load` gives them, each in its schema's form.
Steering = dict[str, Any]
# Each status of a step, and of a deliverable, as the steering's schema names them.
STEP = ("open", "trying", "done")
DELIVERABLE = ("open", "done")
# The issues of a run that no pruner has named yet.
_NO_ISSUES: dict[str, list[int]] = {"closes": [], "refs": []}


def taken_in(steering: Steering | None, result: dict[str, Any]) -> Steering:
    """The steering with the pruner's result taken in.

    Takes: the steering as it stands, or None where the run has none yet, and the pruner's result
    in its schema's form.
    Gives: a new steering: the result's tree whole; its issues, else the steering's, else none;
    and its steps, else the steering's, each step that the steering holds for the same need with
    the same words keeping its status, and each of its deliverables at the same path keeping its
    own, every other step and deliverable open; and the inspection passed where the steering
    holds it so and the result adds no step, as a step added grows the pull request.
    Changes: nothing.
    Refuses: nothing.
    """
    state = steering["state"] if steering else {"issues": _NO_ISSUES, "steps": []}
    steps = state["steps"]
    if "steps" in result:
        steps = [_kept(each, state["steps"]) for each in result["steps"]]
    issues = copy.deepcopy(result.get("issues", state["issues"]))
    held = [(each["for"], each["settles"]) for each in state["steps"]]
    added = any((each["for"], each["settles"]) not in held for each in steps)
    inspected = {"inspected": True} if state.get("inspected") and not added else {}
    return {
        "ost": copy.deepcopy(result["ost"]),
        "state": {"issues": issues, "steps": steps, **inspected},
    }


def _kept(step: dict[str, Any], held: list[dict[str, Any]]) -> dict[str, Any]:
    same = next(
        (each for each in held if (each["for"], each["settles"]) == (step["for"], step["settles"])),
        None,
    )
    had = {each["path"]: each["status"] for each in same["deliverables"]} if same else {}
    return {
        "for": step["for"],
        "settles": step["settles"],
        "deliverables": [
            {"path": each["path"], "kind": each["kind"], "status": had.get(each["path"], "open")}
            for each in step["deliverables"]
        ],
        "status": same["status"] if same else "open",
    }


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


def deliverable_marked(steering: Steering, path: str, status: str) -> Steering:
    """The steering with a deliverable marked.

    Takes: the steering, the deliverable's path as its step names it, and its new status.
    Gives: a new steering with the deliverable at that status in each step that names it, and
    each such step open again where the deliverable goes back to open, as it's made again.
    Changes: nothing.
    Refuses: Wrong where no step names the path, or the status is none of a deliverable's.
    """
    if status not in DELIVERABLE:
        raise Wrong(
            f"{status!r} isn't a deliverable's status; give one of {', '.join(DELIVERABLE)}"
        )
    marked = copy.deepcopy(steering)
    found = False
    for step in marked["state"]["steps"]:
        for each in step["deliverables"]:
            if each["path"] == path:
                each["status"] = status
                found = True
                step["status"] = "open" if status == "open" else step["status"]
    if not found:
        raise Wrong(f"no step names the deliverable {path!r}; give its path as its step names it")
    return marked


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
