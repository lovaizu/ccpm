"""Decides a Record's form on disk, as record.schema.json gives it: each step and practice in the
order recorded, and the result that rn's check kept once it passed the end."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

import json_form
from fault import CantRun, Wrong

# A practice's ID: its condition's ID and its place, such as N6.2.
_PRACTICE = re.compile(r"^N[0-9]+\.[0-9]+$")


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

    Takes: the record's path, and the entry: a step from 1 or a practice whose ID is of the form
    N<n>.<m>, never both, with what it left or gave in one character or more.
    Gives: nothing.
    Changes: the record, made where it isn't there yet, the entry after each one it holds.
    Refuses: fault.Wrong, saying what the entry takes, where the entry or the record leaves the
    form, before it changes anything; fault.CantRun, where it can't be written.
    Carries: S1 `G->>R: records each step and practice as it takes it (Record)`, and the same of
    each role and the orchestrator.
    """
    if (entry.step is None) == (entry.practice is None):
        raise Wrong("an entry is either a step's number or a practice's ID, such as 3 or N6.2")
    if entry.step is not None and entry.step < 1:
        raise Wrong(f"a step's number is 1 or more, not {entry.step}")
    if entry.practice is not None and not _PRACTICE.match(entry.practice):
        raise Wrong(
            f"a practice's ID takes the form N<n>.<m>, such as N6.2, not {entry.practice!r}"
        )
    if not entry.of or not entry.gave:
        raise Wrong("an entry names its prompt or best practice, and what it left or gave")
    held = read(path)
    _write(path, Record((*held.entries, entry), held.kept))


def read(path: str) -> Record:
    """A record.

    Takes: the record's path.
    Gives: the record, with no entries and no result kept where it isn't there yet.
    Changes: nothing.
    Refuses: fault.Wrong, naming the place, where it leaves the form; fault.CantRun, where it can't
    be read.
    Carries: S1 `GD->>R: checks its record`; S5 `A->>R: gets the result kept in each of those
    records (Record)`.
    """
    if not os.path.exists(path):
        return Record((), None)
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        raise CantRun(f"the record {path} can't be read: {e}") from None
    try:
        held = json.loads(text)
    except ValueError as e:
        raise Wrong(f"{path}: isn't JSON: {e}") from None
    json_form.hold(held, json_form.load("record.schema.json"), path)
    entries = tuple(
        Entry(e["of"], e.get("step"), e.get("practice"), e["gave"]) for e in held["entries"]
    )
    kept = held.get("kept")
    return Record(entries, Kept(kept["role"], kept["result"]) if kept else None)


def keep(path: str, kept: Kept) -> None:
    """Keeps the result of a start in its record.

    Takes: the record's path, and the result with its role.
    Gives: nothing.
    Changes: the record, its result kept in place of any kept before.
    Refuses: fault.Wrong, where the record leaves the form; fault.CantRun, where it can't be
    written.
    Carries: S1 `R-->>GD: ... or none, keeping the result in the record`.
    """
    _write(path, Record(read(path).entries, kept))


def _write(path: str, record: Record) -> None:
    entries: list[dict[str, Any]] = [
        {"of": e.of, "step": e.step, "gave": e.gave}
        if e.step is not None
        else {"of": e.of, "practice": e.practice, "gave": e.gave}
        for e in record.entries
    ]
    held: dict[str, Any] = {"entries": entries}
    if record.kept:
        held["kept"] = {"role": record.kept.role, "result": record.kept.result}
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(held, f, indent=2)
            f.write("\n")
    except OSError as e:
        raise CantRun(f"the record {path} can't be written: {e}") from None
