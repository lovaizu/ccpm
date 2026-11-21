"""Decides where each Round of a deliverable lies in the run's folder and what files it holds:
`rounds/<deliverable>/<stage>-<n>/`, the deliverable's path percent-encoded whole, as
`urllib.parse.quote(path, safe="")` gives it, so that no two paths share a folder, holding each
role's Cut and each role's result."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, unquote

from fault import Wrong
from repository.place import RunPlace

# The name of a Round's folder: its stage and its number in the stage from 1.
_NAME = re.compile(r"(content|refactor)-([1-9][0-9]*)")
_STAGES = ("content", "refactor")
# The roles whose files a Round holds.
ROLES = ("generator", "evaluator")

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
        return os.path.join(self.folder, f"{_role(role)}-cut.json")

    def result(self, role: str) -> str:
        """The path of the role's result, `<folder>/<role>.json`, for `generator` or
        `evaluator`. Raises Wrong for another role."""
        return os.path.join(self.folder, f"{_role(role)}.json")


def of(run: RunPlace, deliverable: str) -> list[Round]:
    """Each Round of the deliverable so far.

    Takes: the run, and the deliverable's path.
    Gives: each Round whose folder lies in the run's Rounds, content before refactor, each stage
    by its number; none before the first.
    Changes: nothing.
    Refuses: Wrong where a folder of the deliverable's Rounds has a name of another form, naming
    it.
    """
    top = _folder_of(run, deliverable)
    if not os.path.isdir(top):
        return []
    found = []
    for name in os.listdir(top):
        named = _NAME.fullmatch(name)
        if not named:
            raise Wrong(f"{os.path.join(top, name)}: isn't a Round's folder, <stage>-<n>")
        found.append(Round(os.path.join(top, name), deliverable, named[1], int(named[2])))
    return sorted(found, key=lambda each: (_STAGES.index(each.stage), each.number))


def at(run: RunPlace, folder: str) -> Round:
    """The Round whose folder a script is given.

    Takes: the run, and a Round's folder, from the folder the command runs in or absolute.
    Gives: the Round, its deliverable's path the folder's first name turned back by
    `urllib.parse.unquote`.
    Changes: nothing.
    Refuses: Wrong where the folder isn't a Round's folder of the run, naming it and the form it
    takes.
    """
    path = os.path.abspath(folder)
    top, name = os.path.split(path)
    rounds, encoded = os.path.split(top)
    named = _NAME.fullmatch(name)
    if not named or rounds != os.path.normpath(run.rounds):
        raise Wrong(
            f"{folder}: isn't a Round's folder of the run, which takes the form"
            f" {run.rounds}/<deliverable>/<stage>-<n>"
        )
    return Round(path, unquote(encoded), named[1], int(named[2]))


def new(run: RunPlace, deliverable: str, stage: str) -> Round:
    """The deliverable's next Round of the stage.

    Takes: the run, the deliverable's path, and `content` or `refactor`.
    Gives: the Round numbered one past the stage's last, its folder made.
    Changes: makes the Round's folder.
    Refuses: Wrong where the stage is neither `content` nor `refactor`.
    """
    if stage not in _STAGES:
        raise Wrong(f"a Round's stage is content or refactor, not {stage!r}")
    numbers = [each.number for each in of(run, deliverable) if each.stage == stage]
    number = max(numbers, default=0) + 1
    made = Round(
        os.path.join(_folder_of(run, deliverable), f"{stage}-{number}"), deliverable, stage, number
    )
    os.makedirs(made.folder)
    return made


def result(round_: Round, role: str) -> Result | None:
    """The role's result in the Round.

    Takes: the Round, and `generator` or `evaluator`.
    Gives: the result the role wrote; None where it wrote none yet.
    Changes: nothing.
    Refuses: Wrong where the file isn't JSON, naming it, as check.result holds its form.
    """
    path = round_.result(role)
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return None
    except ValueError as error:
        raise Wrong(f"{path}: isn't JSON: {error}; write the result as JSON") from None


def _folder_of(run: RunPlace, deliverable: str) -> str:
    """The folder of the deliverable's Rounds."""
    return os.path.join(run.rounds, quote(deliverable, safe=""))


def _role(role: str) -> str:
    """The role, refused as Wrong where it's neither generator nor evaluator."""
    if role not in ROLES:
        raise Wrong(f"a Round holds the files of generator and evaluator, not {role!r}")
    return role
