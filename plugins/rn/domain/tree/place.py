"""Decides the form of a Place: the step that one start of a role stands at, by its record, with
the files of its work, kept at each step's end and at a pause."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

import json_form
from fault import CantRun

# The form of a Place's file, as `write` writes it.
_FORM = {
    "type": "object",
    "required": ["record", "step", "work"],
    "additionalProperties": False,
    "properties": {
        "record": {"type": "string"},
        "step": {"type": "integer", "minimum": 1},
        "work": {"type": "array", "items": {"type": "string"}},
    },
}


@dataclass(frozen=True)
class Place:
    """Where one start of a role stands: its record, the step, and each file of its work from the
    worktree."""

    record: str
    step: int
    work: tuple[str, ...]


def write(path: str, place: Place) -> None:
    """Writes a Place.

    Takes: the path of its file, whose folder it makes where it isn't there, and the Place.
    Gives: nothing.
    Changes: the file.
    Refuses: nothing; the round's folder is rn's own, so a fault in writing it stops with its trace.
    Carries: S1 `G->>T: commits its work at the end of each step (Place)`, `E->>T: commits its work
    at the end of each step (Place)`; S4 `O->>T: commits and pushes each role's work so far, with
    the step it stood at (Place)`.
    """
    held = {"record": place.record, "step": place.step, "work": list(place.work)}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(held, f, indent=2)
        f.write("\n")


def read(path: str) -> Place:
    """A Place.

    Takes: the path of its file.
    Gives: the Place.
    Changes: nothing.
    Refuses: fault.Wrong, where the file leaves the form; fault.CantRun, where it can't be read.
    Carries: S5 `O->>G: starts each that stood in a step, at that step (Cut, Place)`, and the same
    of each evaluator.
    """
    try:
        with open(path, encoding="utf-8") as f:
            held = json.load(f)
    except (OSError, ValueError) as e:
        raise CantRun(f"{path} can't be read: {e}") from None
    json_form.hold(held, _FORM, path)
    return Place(held["record"], held["step"], tuple(held["work"]))
