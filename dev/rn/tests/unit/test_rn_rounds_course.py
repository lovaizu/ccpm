"""The unit cases of rounds/course.py, what comes next for a deliverable: its first Round, each
role in turn, each result that asks a judgment weighed first, Rounds again below the limit or with
a remedy, the refactoring once each condition is good or past the limit, the put-up, and a Fix that
is fixed, or that names a decision weighed and then takes Rounds again."""

from __future__ import annotations

from typing import Any

import pytest
from rounds.course import LIMIT, Next, next_of
from rounds.files import CONTENT, FIX, REFACTOR, Entry

MADE = {"result": "made", "files": ["invoice/__main__.py"], "good": []}
POINT = {"result": "point", "point": "Which tax rate? I recommend 10%, as the statement shows."}
GOOD = {"result": "judged", "good": [{"condition": "N1", "lines": ["print"]}], "more": []}
MORE = {"result": "judged", "good": [], "more": [{"condition": "N1", "good_when": "it prints"}]}


def entry(
    stage: str, number: int, weighed: bool = False, decisions: int = 1, **results: Any
) -> Entry:
    return Entry(stage, number, f"/r/{stage}-{number}", decisions, results, weighed)


def test_a_deliverable_with_no_round_starts_one_of_content() -> None:
    """Given a deliverable with no Round.
    When what's next is asked.
    Then a new Round of content."""
    assert next_of([], 1) == Next("new", stage=CONTENT)


@pytest.mark.parametrize(
    ("last", "expected"),
    [
        (entry(CONTENT, 1), "generator"),
        (entry(CONTENT, 1, generator=MADE), "evaluator"),
        (entry(CONTENT, 1, generator=POINT), "weigh"),
        (entry(CONTENT, 1, generator=MADE, evaluator=MORE), "weigh"),
        (entry(REFACTOR, 2), "generator"),
        (entry(FIX, 3), "fixer"),
        (entry(FIX, 3, fixer={"result": "decision", "decision": "d"}), "weigh"),
    ],
    ids=["generator", "evaluator", "point", "findings", "refactor", "fixer", "decision"],
)
def test_each_role_and_each_judgment_comes_in_its_turn_in_the_last_entry(
    last: Entry, expected: str
) -> None:
    """Given a last entry waiting on its generator, its evaluator, a pruner for a point or
    findings, its refactoring's generator, its fixer, or a pruner for a fixer's decision.
    When what's next is asked.
    Then that role or that weighing, in the last entry."""
    assert next_of([last], 1) == Next(expected, last)


def test_a_round_whose_each_condition_is_good_is_refactored() -> None:
    """Given a Round judged with each condition good.
    When what's next is asked.
    Then a new Round of refactoring, with no weighing."""
    assert next_of([entry(CONTENT, 1, generator=MADE, evaluator=GOOD)], 1) == Next(
        "new", stage=REFACTOR
    )


def test_a_weighed_point_starts_a_new_round_of_content() -> None:
    """Given a Round whose generator gave a point, weighed.
    When what's next is asked.
    Then a new Round of content."""
    assert next_of([entry(CONTENT, 1, True, generator=POINT)], 1) == Next("new", stage=CONTENT)


def test_findings_weighed_below_the_limit_take_another_round() -> None:
    """Given a first Round judged with findings, weighed, no remedy written.
    When what's next is asked.
    Then a new Round of content, as the limit isn't reached."""
    assert LIMIT == 2
    assert next_of([entry(CONTENT, 1, True, generator=MADE, evaluator=MORE)], 1) == Next(
        "new", stage=CONTENT
    )


def test_findings_at_the_limit_take_another_round_only_with_a_remedy() -> None:
    """Given two Rounds judged with findings, the last weighed.
    When what's next is asked with no decision added since it started, and with one added.
    Then the refactoring with the findings left, and a new Round of content."""
    made = [
        entry(CONTENT, 1, True, generator=MADE, evaluator=MORE),
        entry(CONTENT, 2, True, decisions=1, generator=MADE, evaluator=MORE),
    ]
    assert next_of(made, 1) == Next("new", stage=REFACTOR)
    assert next_of(made, 2) == Next("new", stage=CONTENT)


def test_a_refactored_deliverable_and_a_fixed_one_are_put_up() -> None:
    """Given a Round of refactoring made, and a Fix fixed.
    When what's next is asked of each.
    Then the put-up."""
    assert next_of([entry(REFACTOR, 2, generator=MADE)], 1) == Next("put-up")
    assert next_of([entry(FIX, 3, fixer={"result": "fixed", "files": []})], 1) == Next("put-up")


def test_a_fixers_decision_weighed_takes_rounds_again() -> None:
    """Given a Fix whose fixer named a decision, weighed.
    When what's next is asked.
    Then a new Round of content."""
    last = entry(FIX, 3, True, fixer={"result": "decision", "decision": "d"})
    assert next_of([last], 2) == Next("new", stage=CONTENT)
