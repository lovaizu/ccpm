"""The layout of each piece's record on disk, a JSON file that each change writes whole, in
`.overnight/<yyyymmdd>-<n>/` at the repository's root."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from pieces.process import Runner

# Where a piece stands, as its runner last recorded it.
State = Literal["running", "waiting", "done", "failed"]

# How a piece's conversation ended, as the runner records it.
Ending = Literal["done", "failed"]


@dataclass(frozen=True)
class Wait:
    """One stretch in which the usage limit held a piece: from its stop to the reset that the
    runner waited for."""

    began: datetime
    resets: datetime


@dataclass(frozen=True)
class Handed:
    """A piece handed over: its number, its folder and branch, and its tools."""

    number: int
    folder: str
    branch: str
    tools: tuple[str, ...]


@dataclass(frozen=True)
class Record:
    """A piece handed over, where it stands, its waits, and its last words, for any later session
    to read."""

    handed: Handed
    state: State
    runner: Runner
    waits: tuple[Wait, ...]
    last_words: str


def highest(repository: str) -> int:
    """The highest number that a record in the repository holds.

    Takes: the repository's root.
    Gives: the highest number of a piece's folder in `.overnight/`, or 0 where there is none.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("pieces.record.highest")


def begin(repository: str, handed: Handed, pid: int) -> Record:
    """Records a piece as running, with the process that carries it as its runner.

    Takes: the repository's root, the piece handed over, and the ID of the runner's process that
    hand-over started.
    Gives: the record, running, with no wait and no last words.
    Changes: writes the record whole, in `.overnight/<yyyymmdd>-<n>/` of today, `<n>` being the
    piece's number.
    Refuses: FileExistsError where a record of the number exists, and LookupError where the
    runner's process no longer runs.
    """
    raise NotImplementedError("pieces.record.begin")


def wait(repository: str, number: int, began: datetime, resets: datetime) -> Record:
    """Records a piece as waiting for the usage limit to reset.

    Takes: the repository's root, the piece's number, when the limit stopped it, and when the
    runner waits until.
    Gives: the record, waiting, with the wait added last.
    Changes: writes the record whole.
    Refuses: LookupError where no record of the number exists.
    """
    raise NotImplementedError("pieces.record.wait")


def resume(repository: str, number: int) -> Record:
    """Records a piece as running again after a wait.

    Takes: the repository's root and the piece's number.
    Gives: the record, running, with its waits kept.
    Changes: writes the record whole.
    Refuses: LookupError where no record of the number exists.
    """
    raise NotImplementedError("pieces.record.resume")


def end(repository: str, number: int, ending: Ending, last_words: str) -> Record:
    """Records a piece as ended: done with its last words, or failed with its error as them.

    Takes: the repository's root, the piece's number, how its conversation ended, and its last
    words or its error.
    Gives: the record, done or failed, with its last words.
    Changes: writes the record whole.
    Refuses: LookupError where no record of the number exists.
    """
    raise NotImplementedError("pieces.record.end")


def read(repository: str) -> list[Record]:
    """Each piece's record in the repository.

    Takes: the repository's root.
    Gives: each record, by its number, or none where `.overnight/` holds none.
    Changes: nothing.
    Refuses: ValueError, naming the file, where a record leaves the layout.
    """
    raise NotImplementedError("pieces.record.read")
