"""Decides how tree.py reads what a role wrote in a round: a generator's Made and an evaluator's
Answers, in the forms that generator-out.schema.json and evaluator-out.schema.json give."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import json_form


@dataclass(frozen=True)
class Settled:
    """A point that a generator settled without asking: the point, what it decided, and its
    ground."""

    point: str
    decided: str
    ground: str


@dataclass(frozen=True)
class Made:
    """What a generator made: where it carries out each decision, by its path, and each More kept,
    by its best practice's kind and its necessary condition's ID, which key it as the kind's best
    practice and the refactor one share condition IDs; and each point it settled without asking,
    with its ground."""

    decisions: Mapping[str, str]
    more: Mapping[tuple[str, str], str]
    settled: tuple[Settled, ...]


@dataclass(frozen=True)
class Answers:
    """One evaluator's answer to each necessary condition of its group: each in good with the lines
    that meet it, or in more with its good_when."""

    good: Mapping[str, tuple[str, ...]]
    more: Mapping[str, str]


def read_made(path: str) -> Made:
    """A generator's Made.

    Takes: the path of the file it wrote.
    Gives: the Made, each place where it makes a More kept good keyed by `(best_practice,
    condition)`.
    Changes: nothing.
    Refuses: fault.Wrong, naming each place, where the file leaves the form; fault.CantRun, where it
    can't be read.
    Carries: S1 `T-->>O: each evaluator's Answers, and what the generator made (Answers, Made)`.
    """
    held = _read(path, "generator-out.schema.json", "made")
    return Made(
        {each["path"]: each["where"] for each in held["decisions"]},
        {(each["best_practice"], each["condition"]): each["where"] for each in held["more"]},
        tuple(Settled(e["point"], e["decided"], e["ground"]) for e in held["settled"]),
    )


def read_answers(path: str) -> Answers:
    """An evaluator's Answers.

    Takes: the path of the file it wrote.
    Gives: the Answers.
    Changes: nothing.
    Refuses: fault.Wrong, naming each place, where the file leaves the form; fault.CantRun, where it
    can't be read.
    Carries: S1 `T-->>O: each evaluator's Answers, and what the generator made (Answers, Made)`.
    """
    held = _read(path, "evaluator-out.schema.json", "answers")
    return Answers(
        {each["question"]: tuple(each["lines"]) for each in held["good"]},
        {each["question"]: each["good_when"] for each in held["more"]},
    )


def _read(path: str, form: str, field: str) -> Any:
    """The JSON in the file at the path, held to the field's form in the role's out-schema."""
    schema = json_form.load(form)["properties"][field]
    return json_form.read(path, schema, os.path.basename(path))
