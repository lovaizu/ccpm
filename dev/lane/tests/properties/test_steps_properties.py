"""The property-based tests of the lane types that hold a role's Steps, as Lane's Test strategy
names each lane type's check: a role marks its Steps and Items and reads its files in orders that
no developer foresees. Each finds no counterexample, by hypothesis, and quality.sh runs them in
CI."""

from __future__ import annotations

import dataclasses
import os
import tempfile
from typing import Any

import lane_data as d
import pytest
from hypothesis import given
from hypothesis import strategies as st
from lanes.keeps_items import TYPE as KEEPS_ITEMS
from lanes.keeps_steps import TYPE as KEEPS_STEPS
from lanes.kind import Held, Kept, Marking
from lanes.reads_none import TYPE as READS_NONE
from lanes.reads_whole import TYPE as READS_WHOLE
from marks import step_due
from place import EndAsked

NAME = st.text("abcdefghijklmnopqrstuvwxyz_", min_size=1, max_size=8)
LAST = 4


def held(reports: tuple[Any, ...] = (), cwd: str = d.REPO) -> Held:
    start = dataclasses.replace(d.start("writer"), reports=reports)
    return Held(d.run(starts=(start,), due=()), start, d.ROOT, d.ROUTES_OF_WRITE, cwd)


@pytest.mark.supports("test_a_mark_of_step_1_begins_a_new_pass")
@given(st.lists(st.integers(1, LAST), max_size=12))
def test_the_step_due_is_the_one_after_the_latest_marked_in_order_since_step_1(
    steps: list[int],
) -> None:
    """Given: writer's Marks of any Steps, in any order, each taken by may_mark's rule: Step 1, or
    the Step due.
    When: step_due gives the Step due, and keeps_steps checks writer's end.
    Then: the Step due follows the count of Marks since the latest Mark of Step 1, and the end is
    kept only where that count reaches the last Step."""
    taken: list[int] = []
    for step in steps:
        since = taken[len(taken) - taken[::-1].index(1) - 1 :] if 1 in taken else []
        if step == 1 or step == len(since) + 1:
            taken.append(step)
    since = taken[len(taken) - taken[::-1].index(1) - 1 :] if 1 in taken else []
    reports = tuple(d.marked(n) for n in taken)
    due = None if len(since) == LAST else len(since) + 1
    assert step_due(reports, LAST) == due
    kept = KEEPS_STEPS.check_end(d.KEEPS_STEPS, EndAsked("Done."), held(reports)) == Kept()
    assert kept is (due is None)


@pytest.mark.supports("test_a_file_read_in_part_leaves_its_step_unmarked")
@given(st.integers(1, 12), st.lists(st.tuples(st.integers(1, 13), st.integers(0, 13)), max_size=4))
def test_reads_whole_keeps_a_mark_only_where_the_reads_cover_each_line(
    count: int, ranges: list[tuple[int, int]]
) -> None:
    """Given: CHANGELOG.md of any number of lines as Read counts them, and Reads of any lines.
    When: reads_whole checks the Mark of writer's step 1.
    Then: it keeps the Mark only where the Reads cover each line of the file."""
    reads = tuple(d.read(first, first + length - 1) for first, length in ranges if length)
    covered = {n for r in reads for n in range(r.first, r.last + 1)}
    with tempfile.TemporaryDirectory() as top:
        os.makedirs(os.path.join(top, ".git"))
        with open(os.path.join(top, "CHANGELOG.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(f"line {n}" for n in range(1, count + 1)))
        verdict = READS_WHOLE.check_mark(d.READS_WHOLE, Marking(1, reads, None), held(cwd=top))
    assert (verdict == Kept()) is set(range(1, count + 1)).issubset(covered)


@pytest.mark.supports("test_a_step_with_an_item_left_goes_back_to_the_step")
@given(st.lists(NAME, max_size=4, unique=True), st.lists(NAME, max_size=6))
def test_keeps_items_keeps_a_mark_only_once_each_item_is_marked(
    items: list[str], marked: list[str]
) -> None:
    """Given: any Items of writer's step 3, and Marks of any IDs since the Step began.
    When: keeps_items checks the Mark of step 3.
    Then: it keeps the Mark only where each Item is among the IDs marked."""
    since = tuple(d.marked(3, each) for each in marked)
    verdict = KEEPS_ITEMS.check_mark(d.KEEPS_ITEMS, Marking(3, since, tuple(items)), held())
    assert (verdict == Kept()) is set(items).issubset(marked)


@pytest.mark.supports("test_a_call_that_reaches_a_path_never_to_read_is_stopped")
@given(st.one_of(st.just("tally.py"), st.lists(NAME, min_size=1, max_size=3).map("/".join)))
def test_reads_none_stops_a_read_only_of_its_path(path: str) -> None:
    """Given: writer's reads_none Lane for `tally.py`, and a Read of any path in tally.
    When: the type judges it.
    Then: it stops the Read only of tally's tally.py, and judges any other."""
    call = d.tool("Read", file_path=f"{d.REPO}/{path}")
    assert READS_NONE.allows(d.READS_NONE, call, held()) is (False if path == "tally.py" else None)
