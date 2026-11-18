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
# Where a result lies: a file's path and a line, or lines, of it, such as README.md:30-41.
WHERE = re.compile(r"^([^\s:]+):([1-9][0-9]*)(?:-([1-9][0-9]*))?$")


@dataclass(frozen=True)
class Entry:
    """One step of a prompt, by its number, or one practice of a best practice, by its ID such as
    N6.2, with the place where its result lies, such as invoicer/lines.py:12."""

    of: str
    step: int | None
    practice: str | None
    where: str


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


def add(path: str, *entries: Entry) -> None:
    """Adds entries to a record.

    Takes: the record's path, and each entry: a step from 1 or a practice whose ID is of the form
    N<n>.<m>, never both, with where its result lies, a path and a line or lines, as `WHERE` gives.
    Gives: nothing.
    Changes: the record, made where it isn't there yet, the entries after each one it holds.
    Refuses: fault.Wrong, saying what an entry takes, where no entry is given, or an entry or the
    record leaves the form, before it changes anything; fault.CantRun, where the record held can't
    be read.
    Carries: S1 `G->>R: records each step and practice as it takes it (Record)`, and the same of
    each role and the orchestrator.
    """
    if not entries:
        raise Wrong("an entry or more, such as 3=README.md:12 or N6.2=tests/test_lines.py:40")
    for entry in entries:
        _hold(entry)
    held = read(path)
    _write(path, Record((*held.entries, *entries), held.kept))


def _hold(entry: Entry) -> None:
    """Refuses an entry out of its form, saying what it takes."""
    if (entry.step is None) == (entry.practice is None):
        raise Wrong("an entry is either a step's number or a practice's ID, such as 3 or N6.2")
    if entry.step is not None and entry.step < 1:
        raise Wrong(f"a step's number is 1 or more, not {entry.step}")
    if entry.practice is not None and not _PRACTICE.match(entry.practice):
        raise Wrong(
            f"a practice's ID takes the form N<n>.<m>, such as N6.2, not {entry.practice!r}"
        )
    if not entry.of:
        raise Wrong("an entry names its prompt or best practice")
    if not WHERE.match(entry.where):
        raise Wrong(
            "an entry names where its result lies as <path>:<line>, such as invoicer/lines.py:12"
            f" or README.md:30-41, not {entry.where!r}"
        )


def read(path: str) -> Record:
    """A record.

    Takes: the record's path.
    Gives: the record, with no entries and no result kept where it isn't there yet.
    Changes: nothing.
    Refuses: fault.Wrong, naming the place, where it leaves the form; fault.CantRun, where it can't
    be read or isn't JSON.
    Carries: S1 `GD->>R: checks its record`; S5 `A->>R: gets the result kept in each of those
    records (Record)`.
    """
    if not os.path.exists(path):
        return Record((), None)
    try:
        with open(path, encoding="utf-8") as f:
            held = json.load(f)
    except (OSError, ValueError) as e:
        raise CantRun(f"the record {path} can't be read: {e}") from None
    json_form.hold(held, json_form.load("record.schema.json"), path)
    entries = tuple(
        Entry(e["of"], e.get("step"), e.get("practice"), e["where"]) for e in held["entries"]
    )
    kept = held.get("kept")
    return Record(entries, Kept(kept["role"], kept["result"]) if kept else None)


def keep(path: str, kept: Kept) -> None:
    """Keeps the result of a start in its record.

    Takes: the record's path, and the result with its role.
    Gives: nothing.
    Changes: the record, its result kept in place of any kept before.
    Refuses: fault.Wrong, where the record leaves the form; fault.CantRun, where it can't be
    read.
    Carries: S1 `R-->>GD: ... or none, keeping the result in the record`.
    """
    _write(path, Record(read(path).entries, kept))


def _write(path: str, record: Record) -> None:
    entries: list[dict[str, Any]] = [
        {"of": e.of, "step": e.step, "where": e.where}
        if e.step is not None
        else {"of": e.of, "practice": e.practice, "where": e.where}
        for e in record.entries
    ]
    held: dict[str, Any] = {"entries": entries}
    if record.kept:
        held["kept"] = {"role": record.kept.role, "result": record.kept.result}
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(held, f, indent=2)
        f.write("\n")
