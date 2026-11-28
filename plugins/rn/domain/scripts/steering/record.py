"""Decides what each change makes of the work's steering: the orchestrator's aim taken in, the tree,
the tasks, and the decisions whole, each task that the steering already holds by its id keeping
where it is on its way, unless the aim says what it takes next, each new task given the next id,
and each left out canceled; each task moved on by the result of its next role, where nothing is to
weigh, and completed once it's done; and the stage that the work reaches once no task is left,
which belongs to the target."""

from __future__ import annotations

import copy
from typing import Any

from fault import Wrong

# A steering, and the orchestrator's aim, as `json.load` gives them, each in its schema's form.
Steering = dict[str, Any]
# Each stage of the work once no task is left, as the steering's schema names them.
STAGE = ("trying", "enough", "inspected")
# How many evaluated Rounds of content a task takes at most, as remaking that brings no remedy has a
# limit (the architecture's P3.3). What they leave is weighed by the orchestrator.
LIMIT = 2
# What a task keeps of where it is on its way, as the steering's schema names it.
_WAY = ("next", "evaluated", "entry")


def taken_in(
    steering: Steering | None, aim: dict[str, Any], closed: list[dict[str, Any]]
) -> tuple[Steering, list[dict[str, Any]]]:
    """The steering with the orchestrator's aim taken in, and each task that it cancels.

    Takes: the steering as it stands, or None where the work has none yet, the aim in its
    schema's form, and the work's closed tasks.
    Gives: a new steering: the aim's tree, tasks, and decisions; each task of the aim with an id
    keeping where the steering holds it on its way; each new one with the next id, one past the
    highest that the steering and the closed tasks hold, as an id is never given again; each
    task whose next the aim says taking it with no entry, as its next role starts its own; and
    the steering's stage kept where the aim keeps its target, as a new target is handed over anew.
    Then each task that the steering holds and the aim leaves out, as the steering held it, with
    `closed` canceled.
    Changes: nothing.
    Refuses: Wrong where an aim's id names no task that the steering holds, naming the id, or
    where it would make a task again past LIMIT evaluated Rounds, naming the task and what it
    takes instead.
    """
    held = {each["id"]: each for each in (steering["tasks"] if steering else [])}
    last = max((int(each["id"]) for each in [*held.values(), *closed]), default=0)
    tasks = []
    for each in aim["tasks"]:
        if "id" in each and each["id"] not in held:
            raise Wrong(
                f"no task left has the id {each['id']}; give a task that's left by its id, and a"
                " new one with no id"
            )
        if "id" not in each:
            last += 1
        tasks.append(_task(each, held.get(each.get("id", "")), f"{last:03d}"))
    kept = {each["id"] for each in tasks}
    canceled = [{**each, "closed": "canceled"} for key, each in held.items() if key not in kept]
    stage = {}
    if steering and "stage" in steering and _same_target(steering["ost"], aim["ost"]):
        stage = {"stage": steering["stage"]}
    told = {
        "ost": copy.deepcopy(aim["ost"]),
        "tasks": tasks,
        "decisions": list(aim["decisions"]),
        **stage,
    }
    return told, canceled


def target(opportunities: list[dict[str, Any]]) -> str | None:
    """The words of the solution that the work aims at, found anywhere in the tree, else None."""
    found = aimed(opportunities)
    return None if found is None else str(found["solution"])


def aimed(opportunities: list[dict[str, Any]]) -> dict[str, Any] | None:
    """The solution that the work aims at, with its assumptions, found anywhere in the tree, else
    None."""
    for each in opportunities:
        for solution in each.get("solutions", []):
            if solution.get("target"):
                return solution
        found = aimed(each.get("children", []))
        if found is not None:
            return found
    return None


def _same_target(held: dict[str, Any], told: dict[str, Any]) -> bool:
    return target(held["opportunities"]) == target(told["opportunities"])


def _task(told: dict[str, Any], had: dict[str, Any] | None, new: str) -> dict[str, Any]:
    """The task as the aim names it, with its id, or the new one, keeping where the steering
    holds it on its way, and taking what the aim says it takes next."""
    kept = {"id": told.get("id", new)}
    kept.update({key: told[key] for key in ("task", "kind", "refactor") if key in told})
    if had:
        kept.update({key: had[key] for key in _WAY if key in had})
    said = told.get("next")
    if said is None:
        return kept
    for key in ("next", "entry"):
        kept.pop(key, None)
    if said == "generator" and kept.get("evaluated", 0) >= LIMIT:
        raise Wrong(
            f"task {kept['id']} has had its {LIMIT} evaluated Rounds; say fixer to mend what they"
            " left, or leave it out and give a new task to make it again from its first Round"
        )
    return {**kept, "next": said}


def moved(
    steering: Steering, results: dict[str, dict[str, dict[str, Any]]]
) -> tuple[Steering, list[dict[str, Any]]]:
    """The steering with each task moved on by the result of its next role, and each task that
    it completes.

    Takes: the steering, and for each task's id, the results that its entry holds, by role.
    Gives: a new steering in which each task whose next role's result is there takes what follows
    it: a generator's made, its evaluator; a point, a generator's, a fixer's, or a refactorer's,
    the orchestrator's weighing; an evaluator's result, one more evaluated Round, then its weighing
    of what it found, else what follows a task made; a fixer's made, what follows a task made; a
    refactorer's made, its end. What follows a task made is its refactorer, where the task gives
    it a `refactor`, else its end. A task that ends goes, and comes after the steering as it last
    stood, with `closed` completed. Each other task stays as it is.
    Changes: nothing.
    Refuses: nothing.
    """
    marked = copy.deepcopy(steering)
    left, completed = [], []
    for each in marked["tasks"]:
        role = each.get("next", "generator")
        found = results.get(each["id"], {}).get(role) if "entry" in each else None
        if found is None or not _ended(each, role, found):
            left.append(each)
        else:
            completed.append({**each, "closed": "completed"})
    marked["tasks"] = left
    return marked, completed


def _ended(each: dict[str, Any], role: str, found: dict[str, Any]) -> bool:
    """Moves the task on by its next role's result, and says whether that ends it."""
    if found["result"] == "point":
        each["next"] = "weigh"
        return False
    if role == "generator":
        each["next"] = "evaluator"
        return False
    if role == "evaluator":
        each["evaluated"] = each.get("evaluated", 0) + 1
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
