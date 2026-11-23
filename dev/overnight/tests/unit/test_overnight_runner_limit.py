"""The unit cases of runner/limit.py, how a task waits at the usage limit: `resume_at`, at the first
stop, at the sixth and the seventh, which end the two classes, and of a reset that a day's end or an
offset from UTC other than the computer's meets."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from overnight_bench import RESET, WENT_ON
from runner.limit import resume_at

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


@pytest.mark.supports(
    "test_a_task_stopped_by_the_limit_goes_on_in_its_session_two_minutes_after_the_reset"
)
@pytest.mark.parametrize("stops", [1, 6], ids=["first", "sixth"])
def test_a_stop_before_the_seventh_goes_on_two_minutes_after_the_reset(stops: int):
    """Given a reset at 01:40, at the first or the sixth stop
    When when the task goes on is found
    Then it is 01:42"""
    assert resume_at(RESET, stops) == WENT_ON


@pytest.mark.supports(
    "test_the_seventh_stop_at_the_limit_gives_the_task_up_with_why_and_its_session"
)
def test_the_seventh_stop_gives_the_task_up():
    """Given a reset at 01:40, at the seventh stop
    When when the task goes on is found
    Then it is None"""
    assert resume_at(RESET, 7) is None


@pytest.mark.supports(
    "test_a_task_stopped_by_the_limit_goes_on_in_its_session_two_minutes_after_the_reset"
)
def test_a_reset_at_the_days_end_goes_on_the_next_day_in_its_offset():
    """Given a reset at 23:59 in UTC+09:00, at the second stop
    When when the task goes on is found
    Then it is 00:01 of the next day, in UTC+09:00"""
    reset = datetime(2026, 11, 24, 23, 59, tzinfo=timezone(timedelta(hours=9)))

    given = resume_at(reset, 2)

    assert given == datetime(2026, 11, 25, 0, 1, tzinfo=timezone(timedelta(hours=9)))
    assert given is not None and given.utcoffset() == timedelta(hours=9)
