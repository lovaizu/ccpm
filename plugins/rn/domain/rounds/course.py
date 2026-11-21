"""Decides which Round a deliverable takes next: content made until each condition is good, then
refactored until each is good again, each stage at most LIMIT Rounds, none while a point waits on
the user, and after them none, each finding left kept by the orchestrator as an open decision."""

from __future__ import annotations

from collections.abc import Sequence
from typing import NamedTuple, Optional

import practice
from repository.place import RunPlace
from tree.form import Deliverable

from rounds import files
from rounds.files import Result, Round

# The most Rounds of content, and of refactoring, that a deliverable takes, as remaking has a
# limit (the architecture's P3.3).
LIMIT = 2

# A Round so far, with the generator's result and the evaluator's in it, None where the role
# wrote none yet.
Done = tuple[Round, Optional[Result], Optional[Result]]


class Next(NamedTuple):
    """What a deliverable waits on, with the stage, `content` or `refactor`, of the Round where a
    role is to start: `generator`, in a new Round or, where `resumes`, the last Round again;
    `evaluator`, in the last Round; `answer`, the user's answer to an open decision;
    `orchestrator`, to keep each finding left past the limit as an open decision; or `sign-off`."""

    waits_on: str
    stage: str | None
    resumes: bool


def next_of(deliverable: Deliverable, rounds: Sequence[Done], refactors: bool) -> Next:
    """What the deliverable waits on, from its node of the design tree and its Rounds so far.

    Takes: the deliverable's open node, each of its Rounds in order with their results, and
    whether its kind is refactored, as `practice.refactoring` gives a kind.
    Gives, the first that holds:
    - the sign-off, where the last Round's stage has LIMIT Rounds, each with both results, and
      the node's open decisions keep the findings left, as proposals for the user: each open
      decision of a condition not good is such a proposal;
    - the answer, where a decision of the node is open, its `decided` null, a decision of a
      condition good past the limit among them;
    - the generator resuming the last Round, where the last generator's result is `point`, as
      the decision that held its point is answered now, or where the last Round holds no
      generator's result, as a pause stopped it, starting again from its files and spending no
      Round of the limit;
    - the evaluator in the last Round, where the last generator's result is `made` and the
      evaluator's is missing, a pause having stopped it or not;
    - the generator in a new content Round, where there's no Round yet;
    - where a condition of the node isn't good: the generator in a new Round of the last Round's
      stage, where that stage has fewer than LIMIT Rounds, else the orchestrator;
    - where each condition is good: the generator in a new refactor Round, where the kind is
      refactored and it has no refactor Round yet; else the sign-off.
    Changes: nothing.
    Refuses: nothing.
    """
    conditions = deliverable["necessary_conditions"]
    short = {each["id"] for each in conditions if not each["good"]}
    opened = {
        each["id"]
        for each in conditions
        for decision in each["decisions"]
        if decision["decided"] is None
    }
    past = _past(rounds)
    if past and short and opened == short:
        return _SIGN_OFF
    if opened and not (past and opened <= short):
        return Next("answer", None, False)
    if not rounds:
        return Next("generator", "content", False)
    return _after(rounds, short, refactors)


def so_far(run: RunPlace, deliverable: str) -> list[Done]:
    """Each Round of the deliverable so far, as `rounds.files.of` gives them, with each role's
    result in it, as `rounds.files.result` gives it, refused as they refuse."""
    return [
        (each, files.result(each, "generator"), files.result(each, "evaluator"))
        for each in files.of(run, deliverable)
    ]


def next_in(run: RunPlace, deliverable: Deliverable) -> Next:
    """What the deliverable waits on, as `next_of` gives it from its Rounds so far in the run, its
    kind refactored where `practice.refactoring` names a refactoring kind, refused as `so_far`
    refuses."""
    refactors = practice.refactoring(deliverable["kind"]) is not None
    return next_of(deliverable, so_far(run, deliverable["path"]), refactors)


# The sign-off, which a deliverable waits on with no Round to start.
_SIGN_OFF = Next("sign-off", None, False)


def _stage(rounds: Sequence[Done]) -> list[Done]:
    """The Rounds of the last Round's stage."""
    return [each for each in rounds if each[0].stage == rounds[-1][0].stage]


def _past(rounds: Sequence[Done]) -> bool:
    """Whether the last Round's stage has LIMIT Rounds, each with both results."""
    stage = _stage(rounds) if rounds else []
    return len(stage) >= LIMIT and all(made and judged for _, made, judged in stage)


def _after(rounds: Sequence[Done], short: set[str], refactors: bool) -> Next:
    """What the deliverable waits on from its last Round, no point of it waiting on the user."""
    last, made, judged = rounds[-1]
    if made is None or made["result"] == "point":
        return Next("generator", last.stage, True)
    if judged is None:
        return Next("evaluator", last.stage, False)
    if short:
        more = len(_stage(rounds)) < LIMIT
        return Next("generator", last.stage, False) if more else Next("orchestrator", None, False)
    if refactors and not any(each[0].stage == "refactor" for each in rounds):
        return Next("generator", "refactor", False)
    return _SIGN_OFF
