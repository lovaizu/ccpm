"""Decides which Round a deliverable takes next: content made and judged until each condition is
good, at most LIMIT Rounds but where the pruner wrote a remedy since the last one's Cut, then
refactored in a Round that no evaluator judges each time the content leaves each condition good,
none while a point waits on the user, or while a Round's generator's point or evaluator's findings
wait on the pruner's weighing until the tree is committed after them, and after them none, each
finding left kept by the pruner as an open decision; a send-back after a Round put up for the
sign-off starts that course again, and so does the user's answer, as the limit stops a remake asked
by findings that the pruner gave no remedy for, not one asked by the user or by a remedy, each of
which is vital. A Fix after the Rounds, which counts toward no limit, waits on its fixer, then on
the put-up where the fixer fixed it, or on the pruner where it named a decision, until the tree is
committed after it; once the deliverable's decisions change after a Fix, the deliverable takes a
course of Rounds anew, and where they don't, the Fix is over, and the deliverable waits on the
sign-off again."""

from __future__ import annotations

from collections.abc import Sequence
from typing import NamedTuple

import practice
from repository.place import RunPlace
from tree.form import Deliverable

from rounds import files
from rounds.files import Fix, Mark, Result, Round

# The most Rounds of content that a deliverable takes in a course where the pruner wrote no remedy
# since the last one's Cut, as remaking has a limit (the architecture's P3.3). A course takes a
# Round of refactoring, which no evaluator judges, each time its content leaves each condition good
# (P3.2).
LIMIT = 2


class Done(NamedTuple):
    """A Round so far, with the generator's result and the evaluator's in it, None where the role
    wrote none yet, the state it was put up with for the sign-off, None where it wasn't, each
    decision by the user that its generator's Cut held, by its condition's id and its about, and
    each remedy in it, as `remedies` gives them, each None where the Round holds no generator's
    Cut; and whether its last result asks the pruner's judgment, a generator's point or an
    evaluator's findings, that no commit of the tree weighed yet."""

    round: Round
    generator: Result | None
    evaluator: Result | None
    put_up: Mark | None = None
    given: frozenset[tuple[str, str]] | None = None
    remedies: frozenset[tuple[str, str, str]] | None = None
    unweighed: bool = False


class Mend(NamedTuple):
    """A Fix so far, with the fixer's result in it, None where it wrote none yet, the
    deliverable's node that its fixer's Cut held, None where the Fix holds no fixer's Cut, and the
    tree's commit that weighed its fixer's decision, None where none did."""

    fix: Fix
    fixer: Result | None
    given: Deliverable | None
    weighed: str | None = None


class Next(NamedTuple):
    """What a deliverable waits on, with the stage, `content` or `refactor`, of the Round where a
    role is to start, or `fix` for a Fix: `generator`, in a new Round or, where `resumes`, the
    last Round again; `evaluator`, in the last Round, one of content; `fixer`, in the last Fix,
    resuming where its fixer's Cut is written already; `answer`, the user's answer to an open
    decision; `pruner`, to keep each finding left past the limit as an open decision, or, of the
    stage `point`, to weigh the point that the last Round's generator gave, of the stage `judged`,
    to weigh the last Round's evaluator's findings, and of the stage `fix`, to weigh the decision
    that the last Fix's fixer named; or `sign-off`, which a
    deliverable whose Rounds are over, or whose last Fix is fixed, waits on, to be put up and
    signed off."""

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
    - the pruner, of the stage `point` where the last Round's generator's result is `point`, else
      of the stage `judged`, where the last Round is `unweighed`, as its result asks a judgment
      that the tree doesn't hold yet;
    - the sign-off, where the last Round is the course's LIMIT-th or later, of content, each with
      both results, the node holding no remedy that the last Round's generator's Cut didn't, as
      `remedies` gives them, and each condition not good keeps an open
      decision, a finding left as a proposal;
    - the answer, where a decision is open, but where the last Round is that LIMIT-th one and
      each open decision is of a condition not good, a proposal or one the pruner keeps;
    - the generator resuming the last Round, where the last generator's result is `point`, as
      its point is weighed and the tree holds what settles it now, or where the last Round holds no
      generator's result, as a pause stopped it, spending no Round of the limit;
    - the evaluator in the last Round, where it's of content, made, with no evaluator's result;
    - the generator in a new content Round, where there's no Round yet;
    - where a condition isn't good: the generator in a new content Round, where the course has
      fewer than LIMIT Rounds or the node holds a remedy that the last Round's generator's Cut
      didn't, else the pruner, to keep each finding left;
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
    if rounds and rounds[-1].unweighed:
        made = rounds[-1].generator
        return Next("pruner", POINT if made and made["result"] == "point" else JUDGED, False)
    past = _past_limit(deliverable, rounds)
    if past and short and opened == short:
        return _SIGN_OFF
    if opened and not (past and opened <= short):
        return Next("answer", None, False)
    if not rounds:
        return Next("generator", "content", False)
    content = _course(rounds, answers(deliverable))
    return _after(rounds, content, short, refactors, _remedied(deliverable, rounds))


def next_with_fixes(
    deliverable: Deliverable, rounds: Sequence[Done], fixes: Sequence[Mend], refactors: bool
) -> Next:
    """What the deliverable waits on, from its node, its Rounds so far, and its Fixes so far.

    Takes: as `next_of` takes, and each of the deliverable's Fixes in the order they were made,
    with the fixer's result and the node its Cut held, numbered with the Rounds.
    Gives, where the deliverable's last folder is a Fix, the first that holds:
    - the fixer in the Fix, resuming where its Cut is written, where the fixer wrote no result;
    - where the node's necessary conditions differ from those its fixer's Cut held, as a pruner
      changed them since: what `next_of` gives with no Round, a course of Rounds anew;
    - the sign-off, where the fixer's result is `fixed`, for the deliverable to be put up again,
      or where it's `decision` and the tree was committed after it, as the pruner weighed the
      decision and changed nothing, so that the Fix is over;
    - the pruner, of the stage `fix`, where it's `decision` and no commit weighed it yet.
    Else what `next_of` gives from the Rounds after the last Fix, or from each Round where there's
    no Fix, as a Fix ends a course and counts toward no limit.
    Changes: nothing.
    Refuses: nothing.
    """
    last = fixes[-1] if fixes else None
    after = _since_fix(rounds, fixes)
    if last is None or after:
        return next_of(deliverable, after, refactors)
    if last.fixer is None:
        return Next("fixer", FIX, last.given is not None)
    changed = last.given is not None and (
        last.given["necessary_conditions"] != deliverable["necessary_conditions"]
    )
    if changed:
        return next_of(deliverable, [], refactors)
    if last.fixer["result"] == "fixed" or last.weighed is not None:
        return _SIGN_OFF
    return Next("pruner", FIX, False)


def asked(
    deliverable: Deliverable, rounds: Sequence[Done], fixes: Sequence[Mend]
) -> list[dict[str, str]]:
    """Each open decision of the deliverable that waits on the user's answer.

    Takes: as `next_with_fixes` takes, but whether the kind is refactored.
    Gives: each open decision that `held` gives the node, by its condition's id and its about, in
    the node's order, but, where the last Round after the last Fix is the course's LIMIT-th or
    later as `next_of` counts it, those of a condition not good, each a finding left as a
    proposal, which the user meets at the sign-off; none where no decision is open.
    Changes: nothing.
    Refuses: nothing.
    """
    after = _since_fix(rounds, fixes)
    state = held(deliverable)
    proposals = set(state["short"]) if _past_limit(deliverable, after) else set()
    return [each for each in state["open"] if each["condition"] not in proposals]


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


def remedies(deliverable: Deliverable) -> frozenset[tuple[str, str, str]]:
    """Each decision of the deliverable's node settled by other than the user, as the pruner
    writes the remedy of a finding, by its condition's id, its about, and its `decided`."""
    return frozenset(
        (each["id"], decision["about"], decision["decided"])
        for each in deliverable["necessary_conditions"]
        for decision in each["decisions"]
        if decision["decided"] is not None and decision.get("by") != "user"
    )


def so_far(run: RunPlace, deliverable: str) -> list[Done]:
    """Each Round of the deliverable so far, as `rounds.files.of` gives them, with each role's
    result in it, as `rounds.files.result` gives it, the state it was put up with, as
    `rounds.files.marked` gives it, the user's decisions and the remedies in the node its
    generator's Cut held, as `rounds.files.given` gives the node, and unweighed where its
    evaluator's result, or its generator's `point`, lies there with no mark that
    `rounds.files.weighed` reads, refused as they refuse."""
    found: list[Done] = []
    for each in files.of(run, deliverable):
        node = files.given(each)
        made, judged = files.result(each, "generator"), files.result(each, "evaluator")
        asks = judged is not None or (made is not None and made["result"] == "point")
        found.append(
            Done(
                each,
                made,
                judged,
                files.marked(each),
                None if node is None else answers(node),
                None if node is None else remedies(node),
                asks and files.weighed(each) is None,
            )
        )
    return found


def mended(run: RunPlace, deliverable: str) -> list[Mend]:
    """Each Fix of the deliverable so far, as `rounds.files.fixes` gives them, with the fixer's
    result in it, as `rounds.files.fixer_result` gives it, the node its fixer's Cut held, as
    `rounds.files.fixer_given` gives it, and the commit that weighed it, as
    `rounds.files.weighed` gives it, refused as they refuse."""
    return [
        Mend(each, files.fixer_result(each), files.fixer_given(each), files.weighed(each))
        for each in files.fixes(run, deliverable)
    ]


def next_in(run: RunPlace, deliverable: Deliverable) -> Next:
    """What the deliverable waits on, as `next_with_fixes` gives it from its Rounds and its Fixes
    so far in the run, its kind refactored where `practice.refactoring` names a refactoring kind,
    refused as `so_far` and `mended` refuse."""
    refactors = practice.refactoring(deliverable["kind"]) is not None
    path = deliverable["path"]
    return next_with_fixes(deliverable, so_far(run, path), mended(run, path), refactors)


# The stage of a Fix, which a fixer starts in.
FIX = files.FIX
# The stages of the pruner's weighing of a Round's result: a generator's point, and an evaluator's
# findings.
POINT = "point"
JUDGED = "judged"
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


def _since_fix(rounds: Sequence[Done], fixes: Sequence[Mend]) -> list[Done]:
    """The Rounds after the last Fix, or each Round where there's no Fix, as a Fix ends a
    course."""
    last = fixes[-1] if fixes else None
    return [each for each in rounds if last is None or each.round.number > last.fix.number]


def _past_limit(deliverable: Deliverable, rounds: Sequence[Done]) -> bool:
    """Whether the last Round is the course's LIMIT-th or later, of content, each with both
    results, the node holding no remedy that its generator's Cut didn't."""
    content = _course(rounds, answers(deliverable))
    return _past(rounds, content) and not _remedied(deliverable, rounds)


def _answered(round_: Done, answers: frozenset[tuple[str, str]]) -> bool:
    """Whether the user answered after the Round: its generator's Cut lacks one of the answers,
    where it has a Cut at all."""
    return round_.given is not None and not answers <= round_.given


def _past(rounds: Sequence[Done], content: Sequence[Done]) -> bool:
    """Whether the last Round is the course's LIMIT-th, of content, each with both results."""
    if len(content) < LIMIT or rounds[-1].round.stage != "content":
        return False
    return all(each.generator and each.evaluator for each in content)


def _remedied(deliverable: Deliverable, rounds: Sequence[Done]) -> bool:
    """Whether the node holds a remedy that the last Round's generator's Cut didn't, as the pruner
    wrote it since; False where the last Round holds no Cut."""
    last = rounds[-1].remedies if rounds else None
    return last is not None and not remedies(deliverable) <= last


def _after(
    rounds: Sequence[Done],
    content: Sequence[Done],
    short: set[str],
    refactors: bool,
    remedied: bool,
) -> Next:
    """What the deliverable waits on from its last Round, no point of it waiting on the user, and
    whether the pruner wrote a remedy since its generator's Cut."""
    last = rounds[-1]
    stage, made = last.round.stage, last.generator
    if made is None or made["result"] == "point":
        return Next("generator", stage, True)
    if stage == "content" and last.evaluator is None:
        return Next("evaluator", stage, False)
    if short:
        more = len(content) < LIMIT or remedied
        return Next("generator", "content", False) if more else Next("pruner", None, False)
    if refactors and stage == "content":
        return Next("generator", "refactor", False)
    return _SIGN_OFF
