"""Decides what comes next for a deliverable from its Rounds and Fixes: content made and judged
until each condition is good, at most LIMIT judged Rounds but where a remedy was written since the
last one started; then a Round of refactoring, which no evaluator judges; then its put-up. A Fix
goes to its fixer, then to its put-up, or, where its mend would change a decision, to a pruner and
then to Rounds again. Each result that asks a judgment, a generator's point, an evaluator's
findings, or a fixer's decision, goes to a pruner before the course goes on."""

from __future__ import annotations

from typing import NamedTuple

from rounds.files import CONTENT, FIX, REFACTOR, Entry

# How many judged Rounds of content a deliverable takes at most, but where a remedy was written
# since the last one started, as remaking that brings no remedy has a limit (the architecture's
# P3.3).
LIMIT = 2


class Next(NamedTuple):
    """What comes next: `generator`, `evaluator`, or `fixer`, for that role in the entry; `weigh`,
    for a pruner to weigh the entry's result; `put-up`; or `new`, for a new entry of the stage,
    whose generator comes next."""

    what: str
    entry: Entry | None = None
    stage: str | None = None


def next_of(made: list[Entry], decisions: int) -> Next:
    """What comes next for the deliverable.

    Takes: its Rounds and Fixes in the order made, and how many decisions the run holds now.
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
        return Next("put-up") if "generator" in last.results else Next("generator", last)
    return _content(made, last, decisions)


def _fix(last: Entry) -> Next:
    fixer = last.results.get("fixer")
    if fixer is None:
        return Next("fixer", last)
    if fixer["result"] == "fixed":
        return Next("put-up")
    return Next("new", stage=CONTENT) if last.weighed else Next("weigh", last)


def _content(made: list[Entry], last: Entry, decisions: int) -> Next:
    generator = last.results.get("generator")
    if generator is None:
        return Next("generator", last)
    if generator["result"] == "point" or "evaluator" in last.results:
        return _judged(made, last, decisions)
    return Next("evaluator", last)


def _judged(made: list[Entry], last: Entry, decisions: int) -> Next:
    evaluator = last.results.get("evaluator")
    if evaluator is not None and not evaluator.get("more"):
        return Next("new", stage=REFACTOR)
    if not last.weighed:
        return Next("weigh", last)
    judged = sum(1 for each in made if each.stage == CONTENT and "evaluator" in each.results)
    if evaluator is None or judged < LIMIT or decisions > last.decisions:
        return Next("new", stage=CONTENT)
    return Next("new", stage=REFACTOR)
