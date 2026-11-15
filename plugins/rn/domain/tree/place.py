"""Decides the form of a Place: the step that one start of a role stands at, by its record, with
the files of its work, kept at each step's end and at a pause."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Place:
    """Where one start of a role stands: its record, the step, and each file of its work from the
    worktree."""

    record: str
    step: int
    work: tuple[str, ...]


def write(path: str, place: Place) -> None:
    """Writes a Place.

    Takes: the path of its file, and the Place.
    Gives: nothing.
    Changes: the file.
    Refuses: fault.CantRun, where it can't be written.
    Carries: S1 `G->>T: commits its work at the end of each step (Place)`, `E->>T: commits its work
    at the end of each step (Place)`; S4 `O->>T: commits and pushes each role's work so far, with
    the step it stood at (Place)`.
    """
    raise NotImplementedError("place.write")


def read(path: str) -> Place:
    """A Place.

    Takes: the path of its file.
    Gives: the Place.
    Changes: nothing.
    Refuses: fault.Wrong, where the file leaves the form; fault.CantRun, where it can't be read.
    Carries: S5 `O->>G: starts each that stood in a step, at that step (Cut, Place)`, and the same
    of each evaluator.
    """
    raise NotImplementedError("place.read")
