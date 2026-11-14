"""The unit cases of tree/touched.py, the nodes a change of the design tree touches, through
`changed` and `touched`."""

from __future__ import annotations

import pytest
from rn_example import GOAL, HINTS, POINT, TYPED
from rn_parts import ANSWERED, OPEN_POINT, hints, typed, walkthrough
from tree.design import Decision, DesignTree
from tree.touched import GOAL as GOAL_NODE
from tree.touched import changed, touched

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")

DECISION_NODE = f"{HINTS} N3: {POINT}"


@pytest.mark.supports(
    "test_the_goal_and_the_plan_written_commit_the_design_tree_with_the_point_open"
)
def test_changed_with_no_tree_before_is_every_node():
    """Given no tree before, and the walkthrough's plan after
    When the nodes changed are asked for
    Then they're the goal, each deliverable, its condition, and its decision, in the tree's order"""
    assert changed(None, walkthrough()) == (
        GOAL_NODE,
        HINTS,
        f"{HINTS} N3",
        DECISION_NODE,
        TYPED,
        f"{TYPED} N1",
    )


@pytest.mark.supports(
    "test_the_users_answer_written_with_its_ground_marks_the_hints_doing_and_checks_the_path_up"
)
def test_changed_names_the_decision_answered_alone():
    """Given the plan with the point open before, and answered after
    When the nodes changed are asked for
    Then the decision is the one node changed"""
    before = walkthrough(hints(OPEN_POINT), typed())
    assert changed(before, walkthrough()) == (DECISION_NODE,)


@pytest.mark.supports(
    "test_the_users_answer_written_with_its_ground_marks_the_hints_doing_and_checks_the_path_up"
)
def test_changed_of_the_same_tree_is_none():
    """Given the walkthrough's plan before and after
    When the nodes changed are asked for
    Then there are none"""
    assert changed(walkthrough(), walkthrough()) == ()


@pytest.mark.supports(
    "test_the_users_answer_written_with_its_ground_marks_the_hints_doing_and_checks_the_path_up"
)
def test_changed_names_a_deliverable_removed_by_its_path():
    """Given the plan before, and the hints alone after
    When the nodes changed are asked for
    Then the typed marker is among them"""
    assert TYPED in changed(walkthrough(), walkthrough(hints(ANSWERED)))


@pytest.mark.supports(
    "test_the_users_answer_written_with_its_ground_marks_the_hints_doing_and_checks_the_path_up"
)
def test_changed_names_the_goal_where_its_words_change():
    """Given the plan before, and the goal reworded after
    When the nodes changed are asked for
    Then the goal is the one node changed"""
    reworded = DesignTree(GOAL + " Also in their CI.", "user", walkthrough().deliverables)
    assert changed(walkthrough(), reworded) == (GOAL_NODE,)


@pytest.mark.supports(
    "test_the_users_answer_written_with_its_ground_marks_the_hints_doing_and_checks_the_path_up"
)
def test_touched_by_a_decision_lists_the_path_up_to_the_goal_first():
    """Given the walkthrough's plan
    When the nodes the answer touches are asked for
    Then they start with its condition, its deliverable, and the goal, in that order"""
    assert touched(walkthrough(), (DECISION_NODE,))[:3] == (f"{HINTS} N3", HINTS, GOAL_NODE)


@pytest.mark.supports(
    "test_write_lists_the_typed_marker_among_the_nodes_a_change_of_the_hints_touches"
)
def test_touched_by_a_decision_of_the_hints_lists_the_typed_marker_that_takes_from_them():
    """Given the walkthrough's plan, the typed marker taking from the hints
    When the nodes the answer touches are asked for
    Then the typed marker is among them"""
    assert TYPED in touched(walkthrough(), (DECISION_NODE,))


@pytest.mark.supports(
    "test_write_lists_the_typed_marker_among_the_nodes_a_change_of_the_hints_touches"
)
def test_touched_by_a_decision_lists_each_later_decision_of_its_deliverable():
    """Given the hints with the answer and a later decision on Decimal under N3
    When the nodes the answer touches are asked for
    Then the Decimal decision is among them"""
    later = Decision("How amounts are typed", "Decimal", "maker")
    tree = walkthrough(hints(ANSWERED, later), typed())
    assert f"{HINTS} N3: How amounts are typed" in touched(tree, (DECISION_NODE,))


@pytest.mark.supports(
    "test_write_lists_the_typed_marker_among_the_nodes_a_change_of_the_hints_touches"
)
def test_touched_by_a_change_of_the_typed_marker_lists_the_hints_it_takes_from():
    """Given the walkthrough's plan
    When the nodes a change of the typed marker touches are asked for
    Then the hints, before it, are among them"""
    assert HINTS in touched(walkthrough(), (TYPED,))


@pytest.mark.supports(
    "test_write_lists_the_typed_marker_among_the_nodes_a_change_of_the_hints_touches"
)
def test_touched_leaves_out_the_nodes_changed_and_lists_each_once():
    """Given the walkthrough's plan
    When the nodes touched by a change of the decision and of its condition are asked for
    Then neither is among them, and no node comes twice"""
    found = touched(walkthrough(), (DECISION_NODE, f"{HINTS} N3"))
    assert DECISION_NODE not in found and f"{HINTS} N3" not in found
    assert len(found) == len(set(found))
