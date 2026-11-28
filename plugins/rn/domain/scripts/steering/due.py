"""Decides what waits now in the work, from its steering alone: the orchestrator's weighing, where
the tree holds no target; else the first task, as the tasks go in order, with the role it takes
next; else, once no task is left, the hand-over of the target, the user's try, the inspection, or
the work's end, by the stage that the work reached."""

from __future__ import annotations

from typing import Any

from steering.record import Steering

# What's due once no task is left, by the stage that the work reached, absent before the hand-over.
_AFTER = {None: "hand-over", "trying": "trying", "enough": "inspect", "inspected": "ended"}


def due(steering: Steering) -> list[str]:
    """What waits now, a line each, its words apart by a tab.

    Takes: the steering, in its schema's form.
    Gives: `weigh` where no solution of the tree is the target; else
    `make\\t<path>\\t<kind>\\t<next>` for the first task, `<next>` the role it takes next, as the
    steering's schema names it; else `hand-over\\t<solution>` before the hand-over,
    `trying\\t<solution>` while it's in the user's hands, `inspect` once they say it's enough, and
    `ended` once the inspection passed, `<solution>` the target's words.
    Changes: nothing.
    Refuses: nothing.
    """
    target = _target(steering["ost"]["opportunities"])
    if target is None:
        return ["weigh"]
    if steering["tasks"]:
        each = steering["tasks"][0]
        return [f"make\t{each['path']}\t{each['kind']}\t{each.get('next', 'generator')}"]
    after = _AFTER[steering.get("stage")]
    return [f"{after}\t{target}" if after in ("hand-over", "trying") else after]


def _target(opportunities: list[dict[str, Any]]) -> str | None:
    """The words of the solution that the work aims at, found anywhere in the tree, else None."""
    for each in opportunities:
        for solution in each.get("solutions", []):
            if solution.get("target"):
                return str(solution["solution"])
        found = _target(each.get("children", []))
        if found is not None:
            return found
    return None
