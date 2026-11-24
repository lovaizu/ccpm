"""Decides where each Round and each Fix of a deliverable lies in the run's folder and what files
it holds: `rounds/<deliverable>/<stage>-<n>/`, the deliverable's path percent-encoded whole, as
`urllib.parse.quote(path, safe="")` gives it, so that no two paths share a folder, `<stage>`
`content` or `refactor` for a Round and `fix` for a Fix, and `<n>` its number among the
deliverable's Rounds and Fixes together in the order they were made. A Round holds each role's Cut
and each role's result, and, once the deliverable is put up for its sign-off after it, the mark
`put-up.json`, the state put up: `{"short": [<the id of each condition not good>], "open":
[{"condition": <its id>, "about": <its about>}, ...]}` for each open decision, each list in order,
which `rounds.course` reads as what the user signs off. A Fix holds the problem that raised it,
`problem.json`, `{"source": <put-up, final-check, or send-back>, "words": <the problem in the
words that raised it>}`, the fixer's Cut, `fixer-cut.json`, the fixer's result, `fixer.json`, and,
once the tree is committed after the fixer named a decision, the mark `weighed.json`,
`{"commit": <the hash of the tree's commit>}`, which `rounds.course` reads as the decision
weighed."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, unquote

from fault import Wrong
from repository.place import RunPlace

# The name of a Round's or a Fix's folder: its stage and its number among the deliverable's Rounds
# and Fixes from 1.
_NAME = re.compile(r"(content|refactor|fix)-([1-9][0-9]*)")
_STAGES = ("content", "refactor")
# The stage of a Fix's folder.
FIX = "fix"
# The roles whose files a Round holds.
ROLES = ("generator", "evaluator")
# The role whose files a Fix holds.
FIXER = "fixer"
# What raised a Fix's problem: a put-up that the repository's checks refused, a finding of the
# final check, or the user's send-back.
SOURCES = ("put-up", "final-check", "send-back")
# The file that marks a Round as put up for the sign-off, with the state put up.
_PUT_UP = "put-up.json"
# The file of a Fix's problem.
_PROBLEM = "problem.json"
# The file that marks a Fix whose fixer named a decision as weighed, with the tree's commit.
_WEIGHED = "weighed.json"

# A role's result, as it writes it in the form of domain/schemas/<role>-round.schema.json.
Result = dict[str, Any]
# The state of a deliverable put up for its sign-off, as the mark `put-up.json` holds it.
Mark = dict[str, Any]
# A Fix's problem, as `problem.json` holds it.
Problem = dict[str, str]


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


@dataclass(frozen=True)
class Fix:
    """One Fix of a deliverable: its folder, the deliverable's path, and its number among the
    deliverable's Rounds and Fixes from 1, in the order they were made."""

    folder: str
    deliverable: str
    number: int

    @property
    def problem(self) -> str:
        """The path of the Fix's problem, `<folder>/problem.json`."""
        return os.path.join(self.folder, _PROBLEM)

    @property
    def cut(self) -> str:
        """The path of the fixer's Cut, `<folder>/fixer-cut.json`."""
        return os.path.join(self.folder, f"{FIXER}-cut.json")

    @property
    def result(self) -> str:
        """The path of the fixer's result, `<folder>/fixer.json`."""
        return os.path.join(self.folder, f"{FIXER}.json")


def of(run: RunPlace, deliverable: str) -> list[Round]:
    """Each Round of the deliverable so far.

    Takes: the run, and the deliverable's path.
    Gives: each Round whose folder lies in the run's Rounds, in the order they were made, by
    their numbers, and none of its Fixes; none before the first.
    Changes: nothing.
    Refuses: Wrong where a folder of the deliverable's Rounds and Fixes has a name of another form,
    or two share a number, naming them.
    """
    return [
        Round(folder, deliverable, stage, number)
        for stage, number, folder in _listed(run, deliverable)
        if stage != FIX
    ]


def fixes(run: RunPlace, deliverable: str) -> list[Fix]:
    """Each Fix of the deliverable so far.

    Takes: the run, and the deliverable's path.
    Gives: each Fix whose folder lies in the run's Rounds, in the order they were made, by their
    numbers, and none of its Rounds; none before the first.
    Changes: nothing.
    Refuses: Wrong where a folder of the deliverable's Rounds and Fixes has a name of another form,
    or two share a number, naming them.
    """
    return [
        Fix(folder, deliverable, number)
        for stage, number, folder in _listed(run, deliverable)
        if stage == FIX
    ]


def _listed(run: RunPlace, deliverable: str) -> list[tuple[str, int, str]]:
    """Each Round and Fix of the deliverable, as its stage, its number, and its folder, by their
    numbers, refused as Wrong where a folder has a name of another form or two share a number."""
    top = _folder_of(run, deliverable)
    if not os.path.isdir(top):
        return []
    found = []
    for name in os.listdir(top):
        named = _NAME.fullmatch(name)
        if not named:
            raise Wrong(
                f"{os.path.join(top, name)}: isn't a Round's or a Fix's folder, <stage>-<n>"
            )
        found.append((named[1], int(named[2]), os.path.join(top, name)))
    found.sort(key=lambda each: each[1])
    for before, after in zip(found, found[1:]):
        if before[1] == after[1]:
            raise Wrong(
                f"{before[2]}, {after[2]}: two folders share the number {after[1]}, which gives"
                " each Round and each Fix of a deliverable once, in the order they were made"
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
    if not named or named[1] == FIX or rounds != os.path.normpath(run.rounds):
        raise Wrong(
            f"{folder}: isn't a Round's folder of the run, which takes the form"
            f" {run.rounds}/<deliverable>/<stage>-<n>"
        )
    return Round(path, unquote(encoded), named[1], int(named[2]))


def new(run: RunPlace, deliverable: str, stage: str) -> Round:
    """The deliverable's next Round of the stage.

    Takes: the run, the deliverable's path, and `content` or `refactor`.
    Gives: the Round of the stage numbered one past the deliverable's last Round or Fix, its folder
    made.
    Changes: makes the Round's folder.
    Refuses: Wrong where the stage is neither `content` nor `refactor`; as `fixes` refuses.
    """
    if stage not in _STAGES:
        raise Wrong(f"a Round's stage is content or refactor, not {stage!r}")
    number = _next_number(run, deliverable)
    made = Round(
        os.path.join(_folder_of(run, deliverable), f"{stage}-{number}"), deliverable, stage, number
    )
    os.makedirs(made.folder)
    return made


def problem(source: str, words: str) -> Problem:
    """A Fix's problem.

    Takes: what raised it, one of SOURCES, and the problem in the words that raised it, as they
    were printed or said.
    Gives: the problem as `problem.json` holds it, the words as given.
    Changes: nothing.
    Refuses: Wrong where the source isn't one of SOURCES, or the words are empty or only spaces,
    saying what it takes.
    """
    if source not in SOURCES:
        raise Wrong(f"a Fix's problem comes from one of {', '.join(SOURCES)}, not {source!r}")
    if not words.strip():
        raise Wrong(
            "the problem's words are empty; give them on stdin, as the refusal printed them or"
            " the user or the final check said them"
        )
    return {"source": source, "words": words}


def new_fix(run: RunPlace, deliverable: str, given: Problem) -> Fix:
    """The deliverable's next Fix.

    Takes: the run, the deliverable's path, and the problem, as `problem` gives it.
    Gives: the Fix numbered one past the deliverable's last Round or Fix, its folder made.
    Changes: makes the Fix's folder, holding the problem as `problem.json`.
    Refuses: Wrong as `fixes` refuses.
    """
    number = _next_number(run, deliverable)
    made = Fix(os.path.join(_folder_of(run, deliverable), f"{FIX}-{number}"), deliverable, number)
    os.makedirs(made.folder)
    with open(made.problem, "w", encoding="utf-8") as file:
        file.write(json.dumps(given) + "\n")
    return made


def problem_of(fix: Fix) -> Problem | None:
    """The Fix's problem, as `new_fix` wrote it; None where there's none. Refuses Wrong where the
    file isn't JSON, naming it."""
    return _read(fix.problem)


def fixer_result(fix: Fix) -> Result | None:
    """The fixer's result in the Fix, as it wrote it in the form of
    domain/schemas/fixer-fix.schema.json; None where it wrote none yet. Refuses Wrong where the
    file isn't JSON, naming it, as check.result holds its form."""
    return _read(fix.result)


def fixer_given(fix: Fix) -> Any:
    """The deliverable's node that the Fix's fixer's Cut held; None where the Fix holds no fixer's
    Cut. Refuses Wrong where the file isn't JSON, naming it."""
    cut = _read(fix.cut)
    return None if cut is None else cut.get("deliverable")


def weigh(fix: Fix, commit: str) -> None:
    """Marks the Fix as weighed by the tree's commit of the hash, writing `<folder>/weighed.json`
    over one there."""
    with open(os.path.join(fix.folder, _WEIGHED), "w", encoding="utf-8") as file:
        file.write(json.dumps({"commit": commit}) + "\n")


def weighed(fix: Fix) -> str | None:
    """The hash of the tree's commit that `weigh` marked the Fix with; None where it isn't marked.
    Refuses Wrong where the file isn't JSON, naming it."""
    mark = _read(os.path.join(fix.folder, _WEIGHED))
    return None if mark is None else mark["commit"]


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


def _next_number(run: RunPlace, deliverable: str) -> int:
    """The number one past the deliverable's last Round or Fix, 1 before the first."""
    return max((each[1] for each in _listed(run, deliverable)), default=0) + 1


def _folder_of(run: RunPlace, deliverable: str) -> str:
    """The folder of the deliverable's Rounds."""
    return os.path.join(run.rounds, quote(deliverable, safe=""))


def _role(role: str) -> str:
    """The role, refused as Wrong where it's neither generator nor evaluator."""
    if role not in ROLES:
        raise Wrong(f"a Round holds the files of generator and evaluator, not {role!r}")
    return role
