"""Decides the form of a role's record, and of the orchestrator's, in the form of
`record.schema.json`: each step and practice in the order recorded, and the result that rn's check
accepted at the role's end."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Entry:
    """One entry of a record: the prompt or the best practice it's of, the step's number or the
    practice's ID, such as `3` or `N6.2`, and what it left or gave."""

    of: str
    id: str
    gave: str


@dataclass(frozen=True)
class Record:
    """A record: each Entry in the order recorded, and the result that the check accepted, ""
    until then."""

    entries: tuple[Entry, ...] = ()
    result: str = ""


def add(path: str, entry: Entry) -> Record:
    """Adds the Entry at the end of the record at the path, making the record where there's none,
    and gives the record. Raises Wrong, with what each field takes, where the ID is neither a
    step's number from 1 nor a practice's ID such as `N6.2`, or where `gave` is empty."""
    raise NotImplementedError("record.add")


def load(path: str) -> Record:
    """The record at the path, an empty one where there's none. Raises Wrong where it isn't in the
    form of `record.schema.json`."""
    raise NotImplementedError("record.load")


def keep_result(path: str, result: str) -> None:
    """Keeps the result in the record at the path."""
    raise NotImplementedError("record.keep_result")
