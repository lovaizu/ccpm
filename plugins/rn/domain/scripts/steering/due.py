"""Decides what waits now in a run, from its steering alone: each question for the user, which
holds up the rest; the pruner, where the run has no target and asks nothing; else the first step
not done, as the way goes in order: the user's try where it's trying, the next deliverable to make
where it's open, or the hand-over once each of its deliverables is done; and the final check once
each step is done."""

from __future__ import annotations

from steering.record import Steering


def due(steering: Steering) -> list[str]:
    """What waits now, a line each, its words apart by a tab.

    Takes: the steering, in its schema's form.
    Gives: `question\\t<words>` for each open question, and nothing more where there's one;
    `weigh` where no need is picked and nothing is asked; else, for the first step not done,
    numbered from 1, `trying\\t<n>\\t<settles>`, `make\\t<n>\\t<path>\\t<kind>` for its first
    deliverable not done, or `hand-over\\t<n>\\t<settles>`; else `final-check` once there are
    steps and each is done; and `weigh` where no step is set yet.
    Changes: nothing.
    Refuses: nothing.
    """
    ost = steering["ost"]
    if ost["questions"]:
        return [f"question\t{each}" for each in ost["questions"]]
    steps = steering["state"]["steps"]
    if ost["target"] is None or not steps:
        return ["weigh"]
    for number, step in enumerate(steps, 1):
        if step["status"] != "done":
            return [_of(number, step)]
    return ["final-check"]


def _of(number: int, step: dict) -> str:
    if step["status"] == "trying":
        return f"trying\t{number}\t{step['settles']}"
    for each in step["deliverables"]:
        if each["status"] != "done":
            return f"make\t{number}\t{each['path']}\t{each['kind']}"
    return f"hand-over\t{number}\t{step['settles']}"
