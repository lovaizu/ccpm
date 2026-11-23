"""The property-based test of the check, as overnight's Test strategy names it: the user takes in
each finished task and knows why each other ended, as the product vision's Concept says, so the
check of any queue whose tasks ended counts each finished and each given up, and names each why
(invariant, of Run)."""

from __future__ import annotations

import os

import pytest
from checker.report import tell
from hypothesis import given
from hypothesis import strategies as st
from overnight_generators import LOCAL_MOMENTS, NAMES
from record.runs import Run
from record.store import Standing, Stood
from stacker.queue_file import Task

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")

WHYS = st.sampled_from(
    [
        "the usage limit stopped it 7 times",
        "overnight stopped before the task ended",
        "API Error: 500 Internal server error",
    ]
)


@pytest.mark.supports(
    "test_a_check_after_a_stop_gives_up_the_tasks_left_and_says_how_to_carry_them_on"
)
@given(
    st.lists(
        st.tuples(NAMES, st.none() | WHYS, LOCAL_MOMENTS, st.booleans()),
        min_size=1,
        max_size=6,
        unique_by=lambda each: each[0],
    )
)
def test_any_ended_queue_is_told_with_each_count_and_each_why(tasks: list):
    """Given any queue whose tasks each ended, finished or given up with any why, at any moment,
    writing or not
    When where they stand is told
    Then its first line counts each finished and each given up, and each why is named"""
    queue_file = os.path.join(os.sep, "home", "dev", "overnight", "tonight.json")
    standing = Standing(
        False,
        tuple(
            Stood(
                Task(name, f"/home/dev/overnight/{name}.md", "/home/dev/work", writes),
                Run("given up" if why else "finished", "s", 0, (), None, ended, why),
                f"/home/dev/overnight/tonight/{name}.md",
            )
            for name, why, ended, writes in tasks
        ),
    )

    text = tell(queue_file, standing)

    given_up = sum(1 for _, why, _, _ in tasks if why)
    first = text.split("\n")[0]
    assert first.startswith(f"{len(tasks)} task")
    assert first.endswith(
        f"from {queue_file}: {len(tasks) - given_up} finished, {given_up} given up."
    )
    assert all(why in text for _, why, _, _ in tasks if why)
