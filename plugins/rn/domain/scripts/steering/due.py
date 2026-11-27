"""Decides what waits now in a work, from its steering alone: the first question for the user, which
holds up the rest; the pruner, where the work has no target and asks nothing; else the first step
not done, as the way goes in order: the user's try where it's trying, the next deliverable to make
where it's open, with the role it takes next, or the hand-over once each of its deliverables is
done; the inspection once each step is done; and the work's end once the inspection passed."""

from __future__ import annotations

from steering.record import Steering


def due(steering: Steering) -> list[str]:
    """What waits now, a line each, its words apart by a tab.

    Takes: the steering, in its schema's form.
    Gives: `question\\t<words>` for the first open question alone, as the user talks over one at
    a time, and nothing more where there's one;
    `weigh` where no need is picked and nothing is asked; else, for the first step not done,
    numbered from 1, `trying\\t<n>\\t<settles>`, `make\\t<n>\\t<path>\\t<kind>\\t<next>` for its
    first deliverable not done, `<next>` the role it takes next, as the steering's schema names it,
    or `hand-over\\t<n>\\t<settles>`; else, once there are steps and each
    is done, `inspect`, or `ended` where the steering holds the inspection passed; and
    `weigh` where no step is set yet.
    Changes: nothing.
    Refuses: nothing.
    """
    ost = steering["ost"]
    if ost["questions"]:
        return [f"question\t{ost['questions'][0]}"]
    steps = steering["state"]["steps"]
    if ost["target"] is None or not steps:
        return ["weigh"]
    for number, step in enumerate(steps, 1):
        if step["status"] != "done":
            return [_of(number, step)]
    return ["ended"] if steering["state"].get("inspected") else ["inspect"]


def _of(number: int, step: dict) -> str:
    if step["status"] == "trying":
        return f"trying\t{number}\t{step['settles']}"
    for each in step["deliverables"]:
        if each["status"] != "done":
            return (
                f"make\t{number}\t{each['path']}\t{each['kind']}\t{each.get('next', 'generator')}"
            )
    return f"hand-over\t{number}\t{step['settles']}"
