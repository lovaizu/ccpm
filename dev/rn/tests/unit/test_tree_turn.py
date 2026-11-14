"""The unit cases of tree/turn.py, each deliverable whose turn has come, through `due`, `marked`,
and `waiting_work`. Whether a deliverable is due turns on a combination of conditions, so the
cases take one for each combination that can occur, as decision table testing does."""

from __future__ import annotations

import pytest
from rn_example import HINTS, TYPED
from rn_parts import (
    ANSWERED,
    OPEN_POINT,
    PLAN_SIGNED,
    PLAN_WAITING,
    doing,
    done,
    hints,
    typed,
    walkthrough,
)
from tree.design import DOING, Decision
from tree.sign_offs import SIGNED, SignOff
from tree.turn import due, marked, waiting_work

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")


@pytest.mark.supports(
    "test_the_users_answer_written_with_its_ground_marks_the_hints_doing_and_checks_the_path_up"
)
def test_the_hints_are_due_once_the_plan_is_signed_and_their_point_answered():
    """Given the plan signed off, the hints open with their point answered
    When the deliverables due are asked for
    Then the hints alone are due, as the typed marker waits on them"""
    assert due(walkthrough(), PLAN_SIGNED) == (HINTS,)


@pytest.mark.supports("test_no_deliverable_is_marked_doing_before_the_plan_is_signed_off")
def test_none_is_due_while_the_plan_waits_for_its_sign_off():
    """Given the plan put up and waiting
    When the deliverables due are asked for
    Then none is"""
    assert due(walkthrough(), PLAN_WAITING) == ()


@pytest.mark.supports("test_no_deliverable_is_marked_doing_before_the_plan_is_signed_off")
def test_none_is_due_where_the_plan_was_never_put_up():
    """Given no Sign-off at all
    When the deliverables due are asked for
    Then none is"""
    assert due(walkthrough(), ()) == ()


@pytest.mark.supports(
    "test_a_users_point_written_open_keeps_the_deliverable_it_lies_under_from_doing"
)
def test_a_deliverable_with_a_point_open_isnt_due():
    """Given the plan signed off, the hints with their point open
    When the deliverables due are asked for
    Then none is"""
    assert due(walkthrough(hints(OPEN_POINT), typed()), PLAN_SIGNED) == ()


@pytest.mark.supports("test_once_the_hints_are_signed_off_the_typed_marker_is_marked_doing")
def test_the_typed_marker_is_due_once_the_hints_are_done_and_signed_off():
    """Given the plan and the hints signed off, the hints done
    When the deliverables due are asked for
    Then the typed marker is due"""
    signed = (*PLAN_SIGNED, SignOff(HINTS, "", state=SIGNED))
    assert due(walkthrough(done(hints()), typed()), signed) == (TYPED,)


@pytest.mark.supports("test_once_the_hints_are_signed_off_the_typed_marker_is_marked_doing")
def test_the_typed_marker_isnt_due_while_the_hints_done_wait_for_their_sign_off():
    """Given the plan signed off, the hints done and put up, not yet signed
    When the deliverables due are asked for
    Then none is"""
    waiting = (*PLAN_SIGNED, SignOff(HINTS, ""))
    assert due(walkthrough(done(hints()), typed()), waiting) == ()


@pytest.mark.supports("test_once_the_hints_are_signed_off_the_typed_marker_is_marked_doing")
def test_the_typed_marker_isnt_due_while_the_hints_are_doing():
    """Given the plan signed off, the hints doing
    When the deliverables due are asked for
    Then none is"""
    assert due(walkthrough(doing(hints(ANSWERED)), typed()), PLAN_SIGNED) == ()


@pytest.mark.supports(
    "test_the_users_answer_written_with_its_ground_marks_the_hints_doing_and_checks_the_path_up"
)
def test_marked_marks_each_due_deliverable_doing_and_names_it():
    """Given the plan signed off, the hints due
    When the tree is marked
    Then the hints are doing in it, and are the one path marked"""
    tree, paths = marked(walkthrough(), PLAN_SIGNED)
    assert paths == (HINTS,) and tree.deliverables[0].status == DOING
    assert tree.deliverables[1] == typed()


@pytest.mark.supports(
    "test_the_users_answer_written_with_its_ground_marks_the_hints_doing_and_checks_the_path_up"
)
def test_marked_with_none_due_leaves_the_tree_as_it_was():
    """Given the plan waiting
    When the tree is marked
    Then it's the same tree, with no path marked"""
    assert marked(walkthrough(), PLAN_WAITING) == (walkthrough(), ())


@pytest.mark.supports("test_a_second_evaluator_of_the_same_group_isnt_due_beside_the_first")
def test_waiting_work_leaves_out_the_deliverable_a_role_running_works_on():
    """Given the hints and the typed marker both doing, and a role running on the hints
    When the work that waits is asked for
    Then it's the typed marker alone"""
    tree = walkthrough(doing(hints(ANSWERED)), doing(typed(Decision("x", "y", "maker"))))
    assert waiting_work(tree, (HINTS,)) == (TYPED,)


@pytest.mark.supports("test_the_guard_names_the_generators_start_with_the_text_the_adapter_gives")
def test_waiting_work_with_nothing_running_is_each_deliverable_doing():
    """Given the hints doing and the typed marker open
    When the work that waits is asked for, with nothing running
    Then it's the hints"""
    assert waiting_work(walkthrough(doing(hints(ANSWERED)), typed()), ()) == (HINTS,)
