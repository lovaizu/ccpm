"""Decides how rn's check reads a best practice's practices from its `best-practice.json`: each
practice's ID, and whether it's taken while deciding or while making."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from enum import Enum

from fault import CantRun, Wrong


class Phase(Enum):
    """When a practice is carried out, as its mark names."""

    DECIDE = "decide"
    MAKE = "make"


@dataclass(frozen=True)
class Practice:
    """One practice: its ID, such as N6.2, and its phase."""

    id: str
    phase: Phase


def practices(folder: str) -> tuple[Practice, ...]:
    """Each practice of a best practice.

    Takes: the best practice's folder.
    Gives: each practice, in the order of its conditions and items, the item's place from 1.
    Changes: nothing.
    Refuses: fault.Wrong, where best-practice.json leaves its form; fault.CantRun, where it can't be
    read or isn't JSON.
    Carries: S1 `GD->>R: checks its record`, against the practices of the role's best practices.
    """
    path = os.path.join(folder, "best-practice.json")
    try:
        with open(path, encoding="utf-8") as f:
            held = json.load(f)
    except (OSError, ValueError) as e:
        raise CantRun(f"the best practice {path} can't be read: {e}") from None
    try:
        return tuple(
            Practice(f"{condition['id']}.{number}", Phase(item["at"]))
            for factor in held["goal"]["critical_success_factors"]
            for condition in factor["necessary_conditions"]
            for number, item in enumerate(condition["items"], 1)
        )
    except (KeyError, TypeError, ValueError) as e:
        raise Wrong(f"{path}: leaves the form of a best practice at {e!r}") from None
