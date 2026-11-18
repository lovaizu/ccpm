"""The state transition cases of marks.py: each state of a role's pass on its Steps, as its Marks
bring it about, with each run of step.py, item.py, or a Read that can come next, a Step that the
state doesn't expect included: whether `may_mark` takes the Step, and, where the Mark is added,
the Step that `step_due` gives after it and the Reads and Marks that `since_step_began` gives."""

from __future__ import annotations

from typing import Any, NamedTuple

import lane_data as d
import pytest
from marks import may_mark, since_step_began, step_due

LAST = 4

# Each state of a pass of a role of four Steps, by its Marks.
NONE_MARKED: tuple[Any, ...] = ()
MID_PASS = (d.marked(1), d.marked(2))
PASS_DONE = (d.marked(1), d.marked(2), d.marked(3), d.marked(4))
NEW_PASS = (*PASS_DONE, d.marked(1))


class Took(NamedTuple):
    """What a run of step.py for a Step leaves: whether `may_mark` takes it, and, where it does,
    the Step due after its Mark is added; None where none is due."""

    taken: bool
    due_after: int | None


def took(state: tuple[Any, ...], step: int) -> Took:
    """Whether the Step may be marked in the state, and the Step due once its Mark is added."""
    if not may_mark(state, step, LAST):
        return Took(False, step_due(state, LAST))
    return Took(True, step_due((*state, d.marked(step)), LAST))


@pytest.mark.supports(
    "test_a_step_marked_out_of_order_is_stopped_with_the_step_due",
    "test_a_step_marked_in_its_turn_is_added_for_the_subagents_start",
    "test_a_mark_of_step_1_begins_a_new_pass",
)
@pytest.mark.parametrize(
    ("state", "step", "then"),
    [
        pytest.param(NONE_MARKED, 1, Took(True, 2), id="none-marked-step-1"),
        pytest.param(NONE_MARKED, 2, Took(False, 1), id="none-marked-a-step-ahead"),
        pytest.param(NONE_MARKED, 5, Took(False, 1), id="none-marked-a-step-past-the-last"),
        pytest.param(MID_PASS, 3, Took(True, 4), id="mid-pass-the-step-due"),
        pytest.param(MID_PASS, 2, Took(False, 3), id="mid-pass-the-step-marked-last-again"),
        pytest.param(MID_PASS, 4, Took(False, 3), id="mid-pass-a-step-ahead"),
        pytest.param(MID_PASS, 1, Took(True, 2), id="mid-pass-step-1"),
        pytest.param(PASS_DONE, 4, Took(False, None), id="pass-done-the-last-step-again"),
        pytest.param(PASS_DONE, 5, Took(False, None), id="pass-done-a-step-past-the-last"),
        pytest.param(PASS_DONE, 1, Took(True, 2), id="pass-done-step-1"),
        pytest.param(NEW_PASS, 2, Took(True, 3), id="new-pass-the-step-due"),
        pytest.param(NEW_PASS, 3, Took(False, 2), id="new-pass-a-step-ahead"),
        pytest.param(NEW_PASS, 1, Took(True, 2), id="new-pass-step-1-again"),
    ],
)
def test_a_step_marked_in_each_state_of_a_pass(
    state: tuple[Any, ...], step: int, then: Took
) -> None:
    """Given: a role of four Steps with none marked, mid-pass after Step 2, with its pass done, or
    with a new pass begun after it.
    When: step.py names Step 1, the Step due, the Step marked last, a Step ahead, or one past the
    last.
    Then: only Step 1, which begins a new pass, and the Step due are taken, each making the next
    Step due, or none after the last; any other leaves the Step due as it stands."""
    assert took(state, step) == then


@pytest.mark.supports(
    "test_a_step_with_an_item_left_goes_back_to_the_step",
    "test_a_step_marked_before_its_file_is_read_whole_goes_back_to_the_step",
)
@pytest.mark.parametrize(
    ("state", "then"),
    [
        pytest.param(NONE_MARKED, 1, id="none-marked"),
        pytest.param(MID_PASS, 3, id="mid-pass"),
        pytest.param(PASS_DONE, None, id="pass-done"),
        pytest.param(NEW_PASS, 2, id="new-pass"),
    ],
)
def test_an_item_or_a_read_in_each_state_moves_no_step(
    state: tuple[Any, ...], then: int | None
) -> None:
    """Given: a pass in each state.
    When: an Item's Mark and a Read come.
    Then: the Step due stays, and since_step_began gives both, as only a Step's Mark ends a Step."""
    reports = (*state, d.marked(then or LAST, "dated"), d.read(1, 7))
    assert step_due(reports, LAST) == then
    assert since_step_began(reports) == reports[len(state) :]
