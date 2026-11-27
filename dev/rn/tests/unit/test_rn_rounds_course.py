"""The unit cases of rounds/course.py, what comes next for a deliverable: its first Round, each
role in turn, each result that asks a judgment weighed first, Rounds again below the limit, the
user's confirming of the findings that the limit leaves, the refactoring once each condition is
good or the findings are confirmed, the end, and a Fix that is fixed and then refactored, or that
names a decision weighed and then takes Rounds again."""

from __future__ import annotations

from typing import Any

import pytest
from rounds.course import LIMIT, Next, next_of
from rounds.files import CONTENT, FIX, REFACTOR, Entry

MADE = {"result": "made", "files": ["invoice/__main__.py"]}
POINT = {"result": "point", "point": "Which tax rate? I recommend 10%, as the statement shows."}
GOOD = {"result": "judged", "good": [{"condition": "N1", "lines": ["print"]}], "more": []}
MORE = {"result": "judged", "good": [], "more": [{"condition": "N1", "good_when": "it prints"}]}


def entry(
    stage: str, number: int, weighed: bool = False, confirmed: bool = False, **results: Any
) -> Entry:
    return Entry(stage, number, f"/r/{stage}-{number}", results, weighed, confirmed)


def test_a_deliverable_with_no_round_starts_one_of_content() -> None:
    """Given a deliverable with no Round.
    When what's next is asked.
    Then a new Round of content."""
    assert next_of([]) == Next("new", stage=CONTENT)


@pytest.mark.parametrize(
    ("last", "expected"),
    [
        (entry(CONTENT, 1), "generator"),
        (entry(CONTENT, 1, generator=MADE), "evaluator"),
        (entry(CONTENT, 1, generator=POINT), "weigh"),
        (entry(CONTENT, 1, generator=MADE, evaluator=MORE), "weigh"),
        (entry(REFACTOR, 2), "refactorer"),
        (entry(FIX, 3), "fixer"),
        (entry(FIX, 3, fixer={"result": "decision", "decision": "d"}), "weigh"),
    ],
    ids=["generator", "evaluator", "point", "findings", "refactorer", "fixer", "decision"],
)
def test_each_role_and_each_judgment_comes_in_its_turn_in_the_last_entry(
    last: Entry, expected: str
) -> None:
    """Given a last entry waiting on its generator, its evaluator, a pruner for a point or
    findings, its refactorer, its fixer, or a pruner for a fixer's decision.
    When what's next is asked.
    Then that role or that weighing, in the last entry."""
    assert next_of([last]) == Next(expected, last)


def test_a_round_whose_each_condition_is_good_is_refactored() -> None:
    """Given a Round judged with each condition good.
    When what's next is asked.
    Then a new Round of refactoring, with no weighing."""
    assert next_of([entry(CONTENT, 1, generator=MADE, evaluator=GOOD)]) == Next(
        "new", stage=REFACTOR
    )


def test_a_weighed_point_starts_a_new_round_of_content() -> None:
    """Given a Round whose generator gave a point, weighed.
    When what's next is asked.
    Then a new Round of content."""
    assert next_of([entry(CONTENT, 1, True, generator=POINT)]) == Next("new", stage=CONTENT)


def test_findings_weighed_below_the_limit_take_another_round() -> None:
    """Given a first Round judged with findings, weighed.
    When what's next is asked.
    Then a new Round of content, as the limit isn't reached."""
    assert LIMIT == 2
    assert next_of([entry(CONTENT, 1, True, generator=MADE, evaluator=MORE)]) == Next(
        "new", stage=CONTENT
    )


def test_findings_at_the_limit_go_to_the_user_then_to_the_refactoring() -> None:
    """Given two Rounds judged with findings, the last weighed, then the same with its findings
    confirmed.
    When what's next is asked of each.
    Then the user's confirming of the last Round, then a new Round of refactoring."""
    first = entry(CONTENT, 1, True, generator=MADE, evaluator=MORE)
    last = entry(CONTENT, 2, True, generator=MADE, evaluator=MORE)
    assert next_of([first, last]) == Next("confirm", last)
    confirmed = entry(CONTENT, 2, True, True, generator=MADE, evaluator=MORE)
    assert next_of([first, confirmed]) == Next("new", stage=REFACTOR)


def test_a_fixed_deliverable_is_refactored_and_a_refactored_one_is_done() -> None:
    """Given a Fix fixed, and a Round of refactoring made.
    When what's next is asked of each.
    Then a new Round of refactoring, and the end."""
    fixed = entry(FIX, 3, fixer={"result": "fixed", "files": []})
    assert next_of([fixed]) == Next("new", stage=REFACTOR)
    assert next_of([entry(REFACTOR, 4, refactorer=MADE)]) == Next("done")


def test_a_fixers_decision_weighed_takes_rounds_again() -> None:
    """Given a Fix whose fixer named a decision, weighed.
    When what's next is asked.
    Then a new Round of content."""
    last = entry(FIX, 3, True, fixer={"result": "decision", "decision": "d"})
    assert next_of([last]) == Next("new", stage=CONTENT)
