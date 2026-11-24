"""Decides which Round a deliverable takes next: content made and judged until each condition is
good, at most LIMIT Rounds, then refactored in a Round that no evaluator judges each time the
content leaves each condition good, none while a
point waits on the user, and after them none, each finding left kept by the pruner as an open
decision; a send-back after a Round put up for the sign-off starts that course again, and so does
the user's answer, as the limit stops a remake asked by findings, not one asked by the user."""

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
    wrote none yet, the state it was put up with for the sign-off, None where it wasn't, and each
    decision by the user that its generator's Cut held, by its condition's id and its about, None
    where the Round holds no generator's Cut."""

    round: Round
    generator: Result | None
    evaluator: Result | None
    put_up: Mark | None = None
    given: frozenset[tuple[str, str]] | None = None


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
    first, and since the last Round whose generator wasn't given each decision by the user that
    the node holds now, as the user answered after it.
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
    content = _course(rounds, answers(deliverable))
    past = _past(rounds, content)
    if past and short and opened == short:
        return _SIGN_OFF
    if opened and not (past and opened <= short):
        return Next("answer", None, False)
    if not rounds:
        return Next("generator", "content", False)
    return _after(rounds, content, short, refactors)


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


def answers(deliverable: Deliverable) -> frozenset[tuple[str, str]]:
    """Each decision of the deliverable's node settled by the user, by its condition's id and its
    about."""
    return frozenset(
        (each["id"], decision["about"])
        for each in deliverable["necessary_conditions"]
        for decision in each["decisions"]
        if decision["decided"] is not None and decision.get("by") == "user"
    )


def so_far(run: RunPlace, deliverable: str) -> list[Done]:
    """Each Round of the deliverable so far, as `rounds.files.of` gives them, with each role's
    result in it, as `rounds.files.result` gives it, the state it was put up with, as
    `rounds.files.marked` gives it, and the user's decisions in the node its generator's Cut
    held, as `rounds.files.given` gives the node, refused as they refuse."""
    found: list[Done] = []
    for each in files.of(run, deliverable):
        node = files.given(each)
        found.append(
            Done(
                each,
                files.result(each, "generator"),
                files.result(each, "evaluator"),
                files.marked(each),
                None if node is None else answers(node),
            )
        )
    return found


def next_in(run: RunPlace, deliverable: Deliverable) -> Next:
    """What the deliverable waits on, as `next_of` gives it from its Rounds so far in the run, its
    kind refactored where `practice.refactoring` names a refactoring kind, refused as `so_far`
    refuses."""
    refactors = practice.refactoring(deliverable["kind"]) is not None
    return next_of(deliverable, so_far(run, deliverable["path"]), refactors)


# The sign-off, which a deliverable waits on with no Round to start.
_SIGN_OFF = Next("sign-off", None, False)


def _course(rounds: Sequence[Done], answers: frozenset[tuple[str, str]]) -> list[Done]:
    """The Rounds of content since the last Round put up for the sign-off, and since the last
    Round that the user answered after."""
    found: list[Done] = []
    for each in rounds:
        if _answered(each, answers):
            found = []
            continue
        if each.round.stage == "content":
            found.append(each)
        if each.put_up is not None:
            found = []
    return found


def _answered(round_: Done, answers: frozenset[tuple[str, str]]) -> bool:
    """Whether the user answered after the Round: its generator's Cut lacks one of the answers,
    where it has a Cut at all."""
    return round_.given is not None and not answers <= round_.given


def _past(rounds: Sequence[Done], content: Sequence[Done]) -> bool:
    """Whether the last Round is the course's LIMIT-th, of content, each with both results."""
    if len(content) < LIMIT or rounds[-1].round.stage != "content":
        return False
    return all(each.generator and each.evaluator for each in content)


def _after(
    rounds: Sequence[Done], content: Sequence[Done], short: set[str], refactors: bool
) -> Next:
    """What the deliverable waits on from its last Round, no point of it waiting on the user."""
    last = rounds[-1]
    stage, made = last.round.stage, last.generator
    if made is None or made["result"] == "point":
        return Next("generator", stage, True)
    if stage == "content" and last.evaluator is None:
        return Next("evaluator", stage, False)
    if short:
        more = len(content) < LIMIT
        return Next("generator", "content", False) if more else Next("pruner", None, False)
    if refactors and stage == "content":
        return Next("generator", "refactor", False)
    return _SIGN_OFF
