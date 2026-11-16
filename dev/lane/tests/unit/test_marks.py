"""The unit cases of marks.py, how a role's Marks stand on its Steps, through `step_due`,
`may_mark`, `since_step_began`, and `items_left`: each pass begun by a Mark of Step 1, the edges
of a pass at its first and last Step, Reads and Marks of Items beside Marks of Steps, and each
Item left."""

from __future__ import annotations

from typing import Any

import lane_data as d
import pytest
from marks import items_left, may_mark, since_step_began, step_due

LAST = 4


@pytest.mark.supports("test_a_step_marked_out_of_order_is_stopped_with_the_step_due")
@pytest.mark.parametrize(
    "reports, due",
    [
        ((), 1),
        ((d.marked(1),), 2),
        ((d.marked(1), d.marked(2), d.marked(3)), 4),
        ((d.marked(1), d.marked(2), d.marked(3), d.marked(4)), None),
        ((d.read(1, 7), d.marked(1, "dated")), 1),
        ((d.marked(1), d.read(1, 7), d.marked(2, "dated")), 2),
    ],
    ids=[
        "no Mark",
        "Step 1 marked",
        "the Step before the last marked",
        "the last Step marked",
        "a Read and an Item's Mark alone",
        "a Read and an Item's Mark after Step 1",
    ],
)
def test_the_step_due_follows_the_step_marked_last(reports: Any, due: int | None) -> None:
    """Given: writer's Marks and Reads, its last Step 4.
    When: step_due gives the Step due.
    Then: it gives 1 with no Mark of a Step, the Step after the one marked last, and None once the
    last Step is marked, counting no Read or Mark of an Item."""
    assert step_due(reports, LAST) == due


@pytest.mark.supports("test_a_mark_of_step_1_begins_a_new_pass")
@pytest.mark.parametrize(
    "reports, due",
    [
        ((*(d.marked(n) for n in range(1, 5)), d.marked(1)), 2),
        ((d.marked(1), d.marked(2), d.marked(1)), 2),
    ],
    ids=["after a whole pass", "within a pass"],
)
def test_a_mark_of_step_1_begins_a_new_pass(reports: Any, due: int) -> None:
    """Given: writer's Marks, with Step 1 marked again after a whole pass or within one.
    When: step_due gives the Step due.
    Then: it gives Step 2, as the latest Mark of Step 1 began a new pass."""
    assert step_due(reports, LAST) == due


@pytest.mark.supports("test_the_skills_mark_lies_on_its_run_with_no_agent_id")
@pytest.mark.parametrize(
    "reports, due", [((), 1), ((d.marked(1),), None)], ids=["no Mark", "its one Step marked"]
)
def test_a_role_of_one_step_is_due_at_it_until_it_is_marked(reports: Any, due: int | None) -> None:
    """Given: a role whose last Step is 1, such as write.
    When: step_due gives the Step due.
    Then: it gives 1 with no Mark, and None once Step 1 is marked."""
    assert step_due(reports, 1) == due


@pytest.mark.supports("test_a_step_marked_out_of_order_is_stopped_with_the_step_due")
@pytest.mark.parametrize(
    "reports, step, may",
    [
        ((), 1, True),
        ((), 2, False),
        ((d.marked(1),), 2, True),
        ((d.marked(1),), 3, False),
        ((d.marked(1), d.marked(2)), 2, False),
        ((d.marked(1), d.marked(2)), 1, True),
        (tuple(d.marked(n) for n in range(1, 5)), 1, True),
        (tuple(d.marked(n) for n in range(1, 5)), 4, False),
    ],
    ids=[
        "Step 1 with no Mark",
        "Step 2 with no Mark",
        "the Step due",
        "the Step after the one due",
        "a Step marked already",
        "Step 1 within a pass",
        "Step 1 after a whole pass",
        "the last Step again after a whole pass",
    ],
)
def test_a_step_may_be_marked_only_when_due_or_as_step_1(
    reports: Any, step: int, may: bool
) -> None:
    """Given: writer's Marks, its last Step 4.
    When: may_mark judges a Mark of the Step.
    Then: it takes Step 1 at any time, as its Mark begins a new pass, and the Step due, and no
    other."""
    assert may_mark(reports, step, LAST) is may


@pytest.mark.supports("test_a_file_read_in_part_leaves_its_step_unmarked")
@pytest.mark.parametrize(
    "reports, since",
    [
        ((d.read(1, 3), d.marked(1, "dated")), (d.read(1, 3), d.marked(1, "dated"))),
        ((d.read(1, 7), d.marked(1), d.read(1, 2)), (d.read(1, 2),)),
        ((d.marked(1), d.marked(2)), ()),
        (
            (d.marked(1), d.marked(2), d.marked(3, "dated"), d.read(4, 7)),
            (d.marked(3, "dated"), d.read(4, 7)),
        ),
    ],
    ids=[
        "no Step marked",
        "after the Mark of Step 1",
        "nothing since the last Mark",
        "an Item's Mark and a Read since",
    ],
)
def test_the_reports_since_the_step_began_follow_the_latest_mark_of_a_step(
    reports: Any, since: Any
) -> None:
    """Given: writer's Marks and Reads.
    When: since_step_began gives those since the Step due began.
    Then: it gives each one after the latest Mark of a Step, Marks of Items among them, or each
    one where no Step is marked."""
    assert since_step_began(reports) == since


@pytest.mark.supports("test_a_step_with_an_item_left_goes_back_to_the_step")
@pytest.mark.parametrize(
    "reports, left",
    [
        ((d.marked(1), d.marked(2)), ("dated", "linked")),
        ((d.marked(2), d.marked(3, "linked")), ("dated",)),
        ((d.marked(2), d.marked(3, "linked"), d.marked(3, "dated")), ()),
        ((d.marked(3, "dated"), d.marked(2)), ("dated", "linked")),
        ((d.marked(2), d.marked(3, "undated")), ("dated", "linked")),
    ],
    ids=[
        "none marked",
        "one marked",
        "each marked, in another order",
        "one marked before the Step began",
        "an ID the adapter doesn't give",
    ],
)
def test_the_items_left_are_those_unmarked_since_the_step_began(reports: Any, left: Any) -> None:
    """Given: writer's Marks, and Step 3's Items `dated` and `linked`, as the adapter gives them.
    When: items_left gives the Items not yet marked.
    Then: it gives each Item with no Mark since the latest Mark of a Step, in the adapter's
    order."""
    assert items_left(reports, ("dated", "linked")) == left
