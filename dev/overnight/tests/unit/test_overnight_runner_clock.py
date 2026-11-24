"""The unit cases of runner/clock.py, the clock that the runner reads and waits on: `now`, with its
time zone; and `wait_until`, of a time past, of the time now, and of a time a moment ahead."""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

import pytest
from runner.clock import now, wait_until

pytestmark = pytest.mark.xfail(strict=True, reason="runner.clock isn't built yet")

# How far a time read may lie from the system's, and how long a wait may overrun.
LEEWAY = timedelta(seconds=2)
AHEAD = timedelta(milliseconds=300)


@pytest.mark.supports("test_a_weekly_limit_is_waited_until_its_day_and_time")
def test_now_is_the_systems_time_with_its_zone():
    """Given the system's clock
    When the time now is read
    Then it carries a time zone, and lies within two seconds of the system's time"""
    read = now()
    assert read.tzinfo is not None and read.utcoffset() is not None
    assert abs(read - datetime.now(timezone.utc)) < LEEWAY


@pytest.mark.supports(
    "test_a_piece_the_limit_stops_twice_goes_on_in_its_conversation_after_each_reset"
)
@pytest.mark.parametrize("before", [timedelta(hours=1), timedelta(0)], ids=["past", "now"])
def test_a_wait_until_a_time_past_or_now_returns_at_once(before: timedelta):
    """Given a time an hour past, or the time now
    When the runner waits until it
    Then the wait returns within two seconds"""
    started = time.monotonic()
    wait_until(now() - before)
    assert time.monotonic() - started < LEEWAY.total_seconds()


@pytest.mark.supports(
    "test_a_piece_the_limit_stops_twice_goes_on_in_its_conversation_after_each_reset"
)
def test_a_wait_until_a_time_ahead_returns_once_the_clock_reads_it():
    """Given a time 300 milliseconds ahead, in UTC, a zone that may differ from the system's
    When the runner waits until it
    Then the wait returns once the clock reads that time or later, and within two seconds"""
    when = datetime.now(timezone.utc) + AHEAD
    started = time.monotonic()
    wait_until(when)
    assert now() >= when
    assert time.monotonic() - started < LEEWAY.total_seconds()
