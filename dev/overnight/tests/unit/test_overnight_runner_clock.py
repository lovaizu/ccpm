"""The unit cases of runner/clock.py, how overnight reads the time and waits: `now`, with its offset
from UTC, and `sleep_until`, of a moment passed, of one a moment ahead, and of one ahead given in
another offset from UTC."""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

import pytest
from runner.clock import now, sleep_until

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


@pytest.mark.supports("test_a_queue_stacked_anew_waits_for_its_start")
def test_now_is_the_computers_moment_with_its_offset():
    """Given the computer's clock
    When the moment is read
    Then it has an offset from UTC, and lies within two seconds of the computer's own"""
    moment = now()

    assert moment.tzinfo is not None
    assert abs(moment - datetime.now(timezone.utc)) < timedelta(seconds=2)


@pytest.mark.supports("test_a_queue_stacked_anew_waits_for_its_start")
def test_a_moment_passed_is_waited_for_not_at_all():
    """Given a moment an hour ago
    When it is waited for
    Then the wait ends within a tenth of a second"""
    began = time.monotonic()

    sleep_until(datetime.now(timezone.utc) - timedelta(hours=1))

    assert time.monotonic() - began < 0.1


@pytest.mark.supports("test_a_queue_stacked_anew_waits_for_its_start")
@pytest.mark.parametrize("offset", [timedelta(0), timedelta(hours=-7)], ids=["UTC", "UTC-07:00"])
def test_a_moment_ahead_is_waited_for_until_it_comes(offset: timedelta):
    """Given a moment half a second ahead, in UTC or in UTC-07:00
    When it is waited for
    Then the wait ends at it, and within a second after it"""
    moment = datetime.now(timezone(offset)) + timedelta(seconds=0.5)
    began = time.monotonic()

    sleep_until(moment)

    assert datetime.now(timezone.utc) >= moment
    assert time.monotonic() - began < 1.5
