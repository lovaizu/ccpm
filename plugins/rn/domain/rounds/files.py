"""Decides where each Round of a deliverable lies in the run's folder and what files it holds:
`rounds/<deliverable>/<stage>-<n>/`, the deliverable's path percent-encoded whole, as
`urllib.parse.quote(path, safe="")` gives it, so that no two paths share a folder, `<n>` its number
among the deliverable's Rounds in the order they were made, holding each role's Cut and each role's
result, and, once the deliverable is put up for its sign-off after it, the mark `put-up.json`, the
state put up: `{"short": [<the id of each condition not good>], "open": [{"condition": <its id>,
"about": <its about>}, ...]}` for each open decision, each list in order, which `rounds.course`
reads as what the user signs off."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, unquote

from fault import Wrong
from repository.place import RunPlace

# The name of a Round's folder: its stage and its number among the deliverable's Rounds from 1.
_NAME = re.compile(r"(content|refactor)-([1-9][0-9]*)")
_STAGES = ("content", "refactor")
# The roles whose files a Round holds.
ROLES = ("generator", "evaluator")
# The file that marks a Round as put up for the sign-off, with the state put up.
_PUT_UP = "put-up.json"

# A role's result, as it writes it in the form of domain/schemas/<role>-round.schema.json.
Result = dict[str, Any]
# The state of a deliverable put up for its sign-off, as the mark `put-up.json` holds it.
Mark = dict[str, Any]


@dataclass(frozen=True)
class Round:
    """One Round of a deliverable: its folder, the deliverable's path, its stage, `content` or
    `refactor`, and its number among the deliverable's Rounds from 1, in the order they were
    made."""

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
    Gives: each Round whose folder lies in the run's Rounds, in the order they were made, by
    their numbers; none before the first.
    Changes: nothing.
    Refuses: Wrong where a folder of the deliverable's Rounds has a name of another form, or two
    share a number, naming them.
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
    found.sort(key=lambda each: each.number)
    for before, after in zip(found, found[1:]):
        if before.number == after.number:
            raise Wrong(
                f"{before.folder}, {after.folder}: two Rounds share the number {after.number},"
                " which gives each Round of a deliverable once, in the order they were made"
            )
    return found


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
    Gives: the Round of the stage numbered one past the deliverable's last Round, its folder made.
    Changes: makes the Round's folder.
    Refuses: Wrong where the stage is neither `content` nor `refactor`.
    """
    if stage not in _STAGES:
        raise Wrong(f"a Round's stage is content or refactor, not {stage!r}")
    numbers = [each.number for each in of(run, deliverable)]
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
    return _read(round_.result(role))


def mark(run: RunPlace, deliverable: str, state: Mark) -> Round | None:
    """Marks the deliverable's last Round as put up for its sign-off, with the state put up.

    Takes: the run, the deliverable's path, and its state as `put-up.json` holds it.
    Gives: the Round marked; None where the deliverable has no Round, such as the plan.
    Changes: writes `<folder>/put-up.json` of the last Round with the state, over one there.
    Refuses: Wrong where a folder of the deliverable's Rounds isn't a Round's, as `of` refuses.
    """
    rounds = of(run, deliverable)
    if not rounds:
        return None
    with open(os.path.join(rounds[-1].folder, _PUT_UP), "w", encoding="utf-8") as file:
        file.write(json.dumps(state) + "\n")
    return rounds[-1]


def marked(round_: Round) -> Mark | None:
    """The state the Round was put up with, as `mark` wrote it; None where it isn't put up.
    Refuses Wrong where the file isn't JSON, naming it."""
    return _read(os.path.join(round_.folder, _PUT_UP))


def given(round_: Round) -> Any:
    """The deliverable's node that the Round's generator's Cut held; None where the Round holds no
    generator's Cut. Refuses Wrong where the file isn't JSON, naming it."""
    cut = _read(round_.cut("generator"))
    return None if cut is None else cut.get("deliverable")


def _read(path: str) -> Any:
    """The JSON of the file, None where there's none, refused as Wrong where it isn't JSON."""
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return None
    except ValueError as error:
        raise Wrong(f"{path}: isn't JSON: {error}; write it as JSON") from None


def _folder_of(run: RunPlace, deliverable: str) -> str:
    """The folder of the deliverable's Rounds."""
    return os.path.join(run.rounds, quote(deliverable, safe=""))


def _role(role: str) -> str:
    """The role, refused as Wrong where it's neither generator nor evaluator."""
    if role not in ROLES:
        raise Wrong(f"a Round holds the files of generator and evaluator, not {role!r}")
    return role
