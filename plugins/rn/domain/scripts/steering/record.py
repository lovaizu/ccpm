"""Decides what each change makes of the work's steering: the orchestrator's aim taken in, the tree,
the tasks, and the decisions whole, each task that the steering already holds at the same path
keeping where it is on its way, unless the aim says what it takes next; each task moved on by the
result of its next role, where nothing is to weigh, and gone once it's done; and the stage that the
work reaches once no task is left, which belongs to the target."""

from __future__ import annotations

import copy
from typing import Any

from fault import Wrong

# A steering, and the orchestrator's aim, as `json.load` gives them, each in its schema's form.
Steering = dict[str, Any]
# Each stage of the work once no task is left, as the steering's schema names them.
STAGE = ("trying", "enough", "inspected")
# How many judged Rounds of content a task takes at most, as remaking that brings no remedy has a
# limit (the architecture's P3.3). What they leave is weighed by the orchestrator.
LIMIT = 2
# What a task keeps of where it is on its way, as the steering's schema names it.
_WAY = ("next", "judged", "entry")


def taken_in(steering: Steering | None, aim: dict[str, Any]) -> Steering:
    """The steering with the orchestrator's aim taken in.

    Takes: the steering as it stands, or None where the work has none yet, and the aim in its
    schema's form.
    Gives: a new steering: the aim's tree, tasks, and decisions; each task that the steering holds
    at the same path, the first not yet taken, keeping where it is on its way; each task whose next
    the aim says taking it with no entry, as its next role starts its own: generator and the judged
    Rounds kept, anew as generator from its first Round, fixer, or refactorer; and the steering's
    stage kept where the aim keeps its target, as a new target is handed over anew.
    Changes: nothing.
    Refuses: Wrong where it would make a task again past LIMIT judged Rounds, naming the task and
    what it takes instead.
    """
    held = list(steering["tasks"]) if steering else []
    tasks = [_task(each, _taken(held, each["path"])) for each in aim["tasks"]]
    stage = {}
    if steering and "stage" in steering and _same_target(steering["ost"], aim["ost"]):
        stage = {"stage": steering["stage"]}
    return {
        "ost": copy.deepcopy(aim["ost"]),
        "tasks": tasks,
        "decisions": list(aim["decisions"]),
        **stage,
    }


def target(opportunities: list[dict[str, Any]]) -> str | None:
    """The words of the solution that the work aims at, found anywhere in the tree, else None."""
    for each in opportunities:
        for solution in each.get("solutions", []):
            if solution.get("target"):
                return str(solution["solution"])
        found = target(each.get("children", []))
        if found is not None:
            return found
    return None


def _same_target(held: dict[str, Any], told: dict[str, Any]) -> bool:
    return target(held["opportunities"]) == target(told["opportunities"])


def _taken(held: list[dict[str, Any]], path: str) -> dict[str, Any] | None:
    """The first task held at the path, taken off the list so that no other task takes it too."""
    for index, each in enumerate(held):
        if each["path"] == path:
            return held.pop(index)
    return None


def _task(told: dict[str, Any], had: dict[str, Any] | None) -> dict[str, Any]:
    """The task as the aim names it, keeping where the steering holds it on its way, and taking
    what the aim says it takes next."""
    kept = {key: told[key] for key in ("task", "path", "kind", "refactor") if key in told}
    if had:
        kept.update({key: had[key] for key in _WAY if key in had})
    said = told.get("next")
    if said is None:
        return kept
    for key in ("next", "entry"):
        kept.pop(key, None)
    if said == "generator" and kept.get("judged", 0) >= LIMIT:
        raise Wrong(
            f"{told['path']} has had its {LIMIT} judged Rounds; say fixer to mend what they left,"
            " or leave the task out"
        )
    if said == "anew":
        kept.pop("judged", None)
        said = "generator"
    return {**kept, "next": said}


def moved(steering: Steering, results: dict[str, dict[str, dict[str, Any]]]) -> Steering:
    """The steering with each task moved on by the result of its next role.

    Takes: the steering, and for each task's path, the results that its entry holds, by role.
    Gives: a new steering in which each task whose next role's result is there takes what follows
    it: a generator's made, its evaluator; a point, a generator's or a refactorer's, the
    orchestrator's weighing; an evaluator's result, one more judged Round, then its weighing of
    what it found, else what follows a task made; a fixer's, what follows a task made; a
    refactorer's made, its end. What follows a task made is its refactorer, where the task gives
    it a `refactor`, else its end. A task that ends goes. Each other task stays as it is, a task
    not yet started among them, as the results of its path are those of the task before it there.
    Changes: nothing.
    Refuses: nothing.
    """
    marked = copy.deepcopy(steering)
    left = []
    for each in marked["tasks"]:
        role = each.get("next", "generator")
        found = results.get(each["path"], {}).get(role) if "entry" in each else None
        if found is None or not _ended(each, role, found):
            left.append(each)
    marked["tasks"] = left
    return marked


def _ended(each: dict[str, Any], role: str, found: dict[str, Any]) -> bool:
    """Moves the task on by its next role's result, and says whether that ends it."""
    if found["result"] == "point":
        each["next"] = "weigh"
        return False
    if role == "generator":
        each["next"] = "evaluator"
        return False
    if role == "evaluator":
        each["judged"] = each.get("judged", 0) + 1
        if found["more"]:
            each["next"] = "weigh"
            return False
    if role == "refactorer" or "refactor" not in each:
        return True
    each["next"] = "refactorer"
    each.pop("entry", None)
    return False


def marked(steering: Steering, stage: str) -> Steering:
    """The steering with the stage that the work reached.

    Takes: the steering, and the stage, one of STAGE.
    Gives: a new steering at that stage.
    Changes: nothing.
    Refuses: Wrong where the stage is none of STAGE.
    """
    if stage not in STAGE:
        raise Wrong(f"{stage!r} isn't a stage of the work; give one of {', '.join(STAGE)}")
    return {**copy.deepcopy(steering), "stage": stage}
