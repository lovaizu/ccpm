"""Decides where each Round of a deliverable lies in the run's folder and what files it holds:
`rounds/<deliverable>/<stage>-<n>/`, the deliverable's path with each `/` as `-`, holding each
role's Cut and each role's result."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from repository.place import RunPlace

# A role's result, as it writes it in the form of domain/schemas/<role>-round.schema.json.
Result = dict[str, Any]


@dataclass(frozen=True)
class Round:
    """One Round of a deliverable: its folder, the deliverable's path, its stage, `content` or
    `refactor`, and its number in that stage from 1."""

    folder: str
    deliverable: str
    stage: str
    number: int

    def cut(self, role: str) -> str:
        """The path of the role's Cut, `<folder>/<role>-cut.json`, for `generator` or
        `evaluator`. Raises Wrong for another role."""
        raise NotImplementedError("rounds.files.Round.cut")

    def result(self, role: str) -> str:
        """The path of the role's result, `<folder>/<role>.json`, for `generator` or
        `evaluator`. Raises Wrong for another role."""
        raise NotImplementedError("rounds.files.Round.result")


def of(run: RunPlace, deliverable: str) -> list[Round]:
    """Each Round of the deliverable so far.

    Takes: the run, and the deliverable's path.
    Gives: each Round whose folder lies in the run's Rounds, content before refactor, each stage
    by its number; none before the first.
    Changes: nothing.
    Refuses: Wrong where a folder of the deliverable's Rounds has a name of another form, naming
    it.
    """
    raise NotImplementedError("rounds.files.of")


def at(run: RunPlace, folder: str) -> Round:
    """The Round whose folder a script is given.

    Takes: the run, and a Round's folder, from the folder the command runs in or absolute.
    Gives: the Round.
    Changes: nothing.
    Refuses: Wrong where the folder isn't a Round's folder of the run, naming it and the form it
    takes.
    """
    raise NotImplementedError("rounds.files.at")


def new(run: RunPlace, deliverable: str, stage: str) -> Round:
    """The deliverable's next Round of the stage.

    Takes: the run, the deliverable's path, and `content` or `refactor`.
    Gives: the Round numbered one past the stage's last, its folder made.
    Changes: makes the Round's folder.
    Refuses: Wrong where the stage is neither `content` nor `refactor`.
    """
    raise NotImplementedError("rounds.files.new")


def result(round_: Round, role: str) -> Result | None:
    """The role's result in the Round.

    Takes: the Round, and `generator` or `evaluator`.
    Gives: the result the role wrote; None where it wrote none yet.
    Changes: nothing.
    Refuses: Wrong where the file isn't JSON, naming it, as check.result holds its form.
    """
    raise NotImplementedError("rounds.files.result")
