"""Decides a Record's form on disk, as record.schema.json gives it: each step and practice in the
order recorded, and the result that rn's check kept once it passed the end."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Entry:
    """One step of a prompt, by its number, or one practice of a best practice, by its ID such as
    N6.2, with what it left or gave."""

    of: str
    step: int | None
    practice: str | None
    gave: str


@dataclass(frozen=True)
class Kept:
    """The result that a start of a role gave, kept once rn's check passed its end."""

    role: str
    result: str


@dataclass(frozen=True)
class Record:
    """What one start of a role, or the orchestrator, carried out, and the result kept."""

    entries: tuple[Entry, ...]
    kept: Kept | None


def add(path: str, entry: Entry) -> None:
    """Adds an entry to a record.

    Takes: the record's path, and the entry.
    Gives: nothing.
    Changes: the record, made where it isn't there yet.
    Refuses: fault.Wrong, where the entry or the record leaves the form; fault.CantRun, where it
    can't be written.
    Carries: S1 `G->>R: records each step and practice as it takes it (Record)`, and the same of
    each role and the orchestrator.
    """
    raise NotImplementedError("form.add")


def read(path: str) -> Record:
    """A record.

    Takes: the record's path.
    Gives: the record, with no entries where it isn't there yet.
    Changes: nothing.
    Refuses: fault.Wrong, where it leaves the form; fault.CantRun, where it can't be read.
    Carries: S1 `GD->>R: checks its record`; S5 `A->>R: gets the result kept in each of those
    records (Record)`.
    """
    raise NotImplementedError("form.read")


def keep(path: str, kept: Kept) -> None:
    """Keeps the result of a start in its record.

    Takes: the record's path, and the result with its role.
    Gives: nothing.
    Changes: the record.
    Refuses: fault.CantRun, where it can't be written.
    Carries: S1 `R-->>GD: ... or none, keeping the result in the record`.
    """
    raise NotImplementedError("form.keep")
