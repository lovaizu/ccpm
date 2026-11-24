"""Decides which Round a deliverable takes next: content made and judged until each condition is
good, at most LIMIT Rounds, then refactored in a Round that no evaluator judges each time the
content leaves each condition good, none while a
point waits on the user, and after them none, each finding left kept by the pruner as an open
decision; a send-back after a Round put up for the sign-off starts that course again."""

from __future__ import annotations

from collections.abc import Sequence
from typing import NamedTuple

import practice
from repository.place import RunPlace
from tree.form import Deliverable

from rounds import files
from rounds.files import Mark, Result, Round

# The most Rounds of content that a deliverable takes in a course, as remaking has a limit (the
# architecture's P3.3). A course takes a Round of refactoring, which no evaluator judges, each time
# its content leaves each condition good (P3.2).
LIMIT = 2


class Done(NamedTuple):
    """A Round so far, with the generator's result and the evaluator's in it, None where the role
    wrote none yet, and the state it was put up with for the sign-off, None where it wasn't."""

    round: Round
    generator: Result | None
    evaluator: Result | None
    put_up: Mark | None = None


class Next(NamedTuple):
    """What a deliverable waits on, with the stage, `content` or `refactor`, of the Round where a
    role is to start: `generator`, in a new Round or, where `resumes`, the last Round again;
    `evaluator`, in the last Round, one of content; `answer`, the user's answer to an open
    decision; `pruner`, to keep each finding left past the limit as an open decision; or
    `sign-off`."""

    waits_on: str
    stage: str | None
    resumes: bool


def next_of(deliverable: Deliverable, rounds: Sequence[Done], refactors: bool) -> Next:
    """What the deliverable waits on, from its node of the design tree and its Rounds so far.

    Takes: the deliverable's open node, each of its Rounds in the order they were made with their
    results, and whether its kind is refactored, as `practice.refactoring` gives a kind. Its
    course is its Rounds of content since its last Round put up for the sign-off, or since the
    first.
    Gives, the first that holds:
    - the sign-off, where the last Round is put up with the state that `held` gives the node, as
      nothing changed since;
    - the sign-off, where the last Round is the course's LIMIT-th, of content, each with both
      results, and each condition not good keeps an open decision, a finding left as a proposal;
    - the answer, where a decision is open, but where the last Round is that LIMIT-th one and
      each open decision is of a condition not good, a proposal or one the pruner keeps;
    - the generator resuming the last Round, where the last generator's result is `point`, as
      the decision that held its point is answered now, or where the last Round holds no
      generator's result, as a pause stopped it, spending no Round of the limit;
    - the evaluator in the last Round, where it's of content, made, with no evaluator's result;
    - the generator in a new content Round, where there's no Round yet;
    - where a condition isn't good: the generator in a new content Round, where the course has
      fewer than LIMIT Rounds, else the pruner, to keep each finding left;
    - where each is good: the generator in a new refactor Round, where the kind is refactored and
      the last Round is of content; else the sign-off.
    Changes: nothing.
    Refuses: nothing.
    """
    state = held(deliverable)
    short = set(state["short"])
    opened = {each["condition"] for each in state["open"]}
    if rounds and rounds[-1].put_up == state:
        return _SIGN_OFF
    past = _past(rounds)
    if past and short and opened == short:
        return _SIGN_OFF
    if opened and not (past and opened <= short):
        return Next("answer", None, False)
    if not rounds:
        return Next("generator", "content", False)
    return _after(rounds, short, refactors)


def held(deliverable: Deliverable) -> Mark:
    """The state of the deliverable that a Round put up for its sign-off holds, in the form of
    `put-up.json` as `rounds.files` names it: the id of each condition not good, and each open
    decision, its `decided` null, by its condition's id and its `about`, each in the node's
    order."""
    conditions = deliverable["necessary_conditions"]
    return {
        "short": [each["id"] for each in conditions if not each["good"]],
        "open": [
            {"condition": each["id"], "about": decision["about"]}
            for each in conditions
            for decision in each["decisions"]
            if decision["decided"] is None
        ],
    }


def so_far(run: RunPlace, deliverable: str) -> list[Done]:
    """Each Round of the deliverable so far, as `rounds.files.of` gives them, with each role's
    result in it, as `rounds.files.result` gives it, and the state it was put up with, as
    `rounds.files.marked` gives it, refused as they refuse."""
    return [
        Done(
            each,
            files.result(each, "generator"),
            files.result(each, "evaluator"),
            files.marked(each),
        )
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


def _course(rounds: Sequence[Done]) -> list[Done]:
    """The Rounds of content since the last Round put up for the sign-off."""
    found: list[Done] = []
    for each in rounds:
        if each.round.stage == "content":
            found.append(each)
        if each.put_up is not None:
            found = []
    return found


def _past(rounds: Sequence[Done]) -> bool:
    """Whether the last Round is the course's LIMIT-th, of content, each with both results."""
    content = _course(rounds)
    if len(content) < LIMIT or rounds[-1].round.stage != "content":
        return False
    return all(each.generator and each.evaluator for each in content)


def _after(rounds: Sequence[Done], short: set[str], refactors: bool) -> Next:
    """What the deliverable waits on from its last Round, no point of it waiting on the user."""
    last = rounds[-1]
    stage, made = last.round.stage, last.generator
    if made is None or made["result"] == "point":
        return Next("generator", stage, True)
    if stage == "content" and last.evaluator is None:
        return Next("evaluator", stage, False)
    if short:
        more = len(_course(rounds)) < LIMIT
        return Next("generator", "content", False) if more else Next("pruner", None, False)
    if refactors and stage == "content":
        return Next("generator", "refactor", False)
    return _SIGN_OFF
