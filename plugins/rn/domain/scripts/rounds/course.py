"""Decides what comes next for a deliverable from its Rounds and Fixes: content made and judged
until each condition is good, at most LIMIT judged Rounds; then, where findings are left, the
user's confirming of them; then a Fix of what the user would have mended; then a Round of
refactoring of the whole, which no evaluator judges; then the deliverable is done. A Fix goes to
its fixer, then to the refactoring, or, where its mend would change a decision, to a pruner and
then to Rounds again. Each result that asks a judgment, a generator's point, an evaluator's
findings, or a fixer's decision, goes to a pruner before the course goes on."""

from __future__ import annotations

from typing import NamedTuple

from rounds.files import CONTENT, FIX, REFACTOR, Entry

# How many judged Rounds of content a deliverable takes at most, as remaking that brings no
# remedy has a limit (the architecture's P3.3). What they leave goes to the user.
LIMIT = 2


class Next(NamedTuple):
    """What comes next: `generator`, `evaluator`, `refactorer`, or `fixer`, for that role in the
    entry; `weigh`, for a pruner to weigh the entry's result; `confirm`, for the user to confirm
    the findings that the entry's evaluator left; `done`; or `new`, for a new entry of the stage,
    whose generator or refactorer comes next."""

    what: str
    entry: Entry | None = None
    stage: str | None = None


def next_of(made: list[Entry]) -> Next:
    """What comes next for the deliverable.

    Takes: its Rounds and Fixes in the order made.
    Gives: what comes next, as the module says, by its last entry.
    Changes: nothing.
    Refuses: nothing.
    """
    if not made:
        return Next("new", stage=CONTENT)
    last = made[-1]
    if last.stage == FIX:
        return _fix(last)
    if last.stage == REFACTOR:
        return Next("done") if "refactorer" in last.results else Next("refactorer", last)
    return _content(made, last)


def _fix(last: Entry) -> Next:
    fixer = last.results.get("fixer")
    if fixer is None:
        return Next("fixer", last)
    if fixer["result"] == "fixed":
        return Next("new", stage=REFACTOR)
    return Next("new", stage=CONTENT) if last.weighed else Next("weigh", last)


def _content(made: list[Entry], last: Entry) -> Next:
    generator = last.results.get("generator")
    if generator is None:
        return Next("generator", last)
    if generator["result"] == "point" or "evaluator" in last.results:
        return _judged(made, last)
    return Next("evaluator", last)


def _judged(made: list[Entry], last: Entry) -> Next:
    evaluator = last.results.get("evaluator")
    if evaluator is not None and not evaluator.get("more"):
        return Next("new", stage=REFACTOR)
    if not last.weighed:
        return Next("weigh", last)
    judged = sum(1 for each in made if each.stage == CONTENT and "evaluator" in each.results)
    if evaluator is None or judged < LIMIT:
        return Next("new", stage=CONTENT)
    return Next("new", stage=REFACTOR) if last.confirmed else Next("confirm", last)
