"""Decides how rn's check reads a best practice's practices from its `best-practice.json`: each
practice's ID, and whether it's taken while deciding or while making."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


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
    Gives: each practice, in the order of its conditions and items.
    Changes: nothing.
    Refuses: fault.Wrong, where best-practice.json leaves its form; fault.CantRun, where it can't be
    read.
    Carries: S1 `GD->>R: checks its record`, against the practices of the role's best practices.
    """
    raise NotImplementedError("practices.practices")
