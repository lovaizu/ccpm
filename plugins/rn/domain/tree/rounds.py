"""Decides where each round of a deliverable keeps its records, `rounds/<deliverable>/<n>/` in the
run's folder, and their forms: the Try record that throwaway.py keeps, what the generator made,
the Answers of each evaluator, each Lack kept for the next round, and the Place of each role at
the end of each step. A deliverable's folder name is its path with each `/` as `--`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

ROUNDS = "rounds"


@dataclass(frozen=True)
class Tried:
    """One command of the deliverable run in a throwaway copy, with its exit code and what it
    printed."""

    command: str
    exit_code: int
    output: str


@dataclass(frozen=True)
class Met:
    """A necessary condition an evaluator found met, with each line of the deliverable that meets
    it."""

    condition: str
    lines: tuple[str, ...]


@dataclass(frozen=True)
class NotMet:
    """A necessary condition an evaluator found not met, with what the people still lack."""

    condition: str
    lacks: str


@dataclass(frozen=True)
class Answers:
    """One evaluator's Answers on its group of necessary conditions, as `answers` of
    `evaluator-out.schema.json` gives them, with each point open that only the user can settle."""

    group: str
    met: tuple[Met, ...] = ()
    not_met: tuple[NotMet, ...] = ()
    open: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Settled:
    """A point that the generator settled without asking, as its cut, the goal, and its best
    practice settle it one way, with what it settled and why."""

    point: str
    decided: str
    ground: str


@dataclass(frozen=True)
class Made:
    """What the generator made, as `made` of `generator-out.schema.json` gives it: the `about` of
    each decision of its cut and the condition of each lack, each with where the deliverable carries
    it out, and each point it settled without asking."""

    decisions: tuple[tuple[str, str], ...] = ()
    lacks: tuple[tuple[str, str], ...] = ()
    settled: tuple[Settled, ...] = ()


@dataclass(frozen=True)
class LackKept:
    """A lack that the orchestrator judged the people fall short by, by its necessary condition,
    which the deliverable's next round gets."""

    condition: str
    lack: str


@dataclass(frozen=True)
class Place:
    """The step that a role of a round stands at, with the paths of the work it has made, and, for
    an evaluator, its group, "" for the generator."""

    role: str
    step: int
    work: tuple[str, ...] = ()
    group: str = ""


@dataclass(frozen=True)
class Round:
    """One round of a deliverable: its number, the Try record's commands, what the generator made,
    None until it ends with `done`, the Answers of each evaluator, each Lack kept for the round
    after it, and each Place, the last one of each role last."""

    deliverable: str
    number: int
    tried: tuple[Tried, ...] = ()
    made: Made | None = None
    answers: tuple[Answers, ...] = ()
    lacks: tuple[LackKept, ...] = ()
    places: tuple[Place, ...] = ()


def folder(run: str, deliverable: str, number: int) -> str:
    """The folder of the deliverable's round in the run's folder."""
    raise NotImplementedError("rounds.folder")


def latest(run: str, deliverable: str) -> int:
    """The number of the deliverable's last round, 0 where it has none."""
    raise NotImplementedError("rounds.latest")


def load(run: str, deliverable: str, number: int) -> Round:
    """The deliverable's round as its folder holds it, with nothing kept where the folder is empty
    or missing. Raises Wrong, naming the file, where a record isn't in its form."""
    raise NotImplementedError("rounds.load")


def parse_answers(given: Any, group: str, where: str) -> Answers:
    """The Answers of the JSON value that an evaluator wrote to the file at `where`, for the group.
    Raises Wrong, naming the field and what `answers` of `evaluator-out.schema.json` takes there,
    where it isn't in that form."""
    raise NotImplementedError("rounds.parse_answers")


def parse_made(given: Any, where: str) -> Made:
    """What the generator made, of the JSON value that it wrote to the file at `where`. Raises
    Wrong, naming the field and what `made` of `generator-out.schema.json` takes there, where it
    isn't in that form, and where a point settled has no ground."""
    raise NotImplementedError("rounds.parse_made")


def keep_try(run: str, deliverable: str, number: int, tried: Tried) -> str:
    """Adds the command tried to the Try record of the deliverable's round, and gives the record's
    path."""
    raise NotImplementedError("rounds.keep_try")


def keep_lack(run: str, deliverable: str, lack: LackKept) -> str:
    """Keeps the lack in the deliverable's last round, for the round after it, and gives the path
    of the file that holds it."""
    raise NotImplementedError("rounds.keep_lack")


def keep_place(run: str, deliverable: str, place: Place) -> str:
    """Keeps the Place in the deliverable's last round, the generator's or that of the evaluator of
    its group, and gives the path of the file that holds it."""
    raise NotImplementedError("rounds.keep_place")
