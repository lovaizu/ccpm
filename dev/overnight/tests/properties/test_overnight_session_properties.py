"""The property-based test of how a session's end reads, as overnight's Test strategy names it: a
task stopped by the limit goes on two minutes after the reset in its reply, as P2.1 says, so a
session that the session limit or the weekly limit stops reads limited until the reset that Claude
Code names, in whatever form it shows it (invariant, of Reply)."""

from __future__ import annotations

import os
import tempfile
from datetime import timedelta

import claude_double
import pytest
from claude_double import Answer
from hypothesis import given
from hypothesis import strategies as st
from overnight_generators import LOCAL_MOMENTS
from session.claude import Output
from session.ending import Limited, ending

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


@pytest.mark.supports(
    "test_a_task_stopped_by_the_limit_goes_on_in_its_session_two_minutes_after_the_reset"
)
@given(
    LOCAL_MOMENTS,
    st.one_of(
        st.tuples(st.just(False), st.integers(1, 5 * 60)),
        st.tuples(st.just(True), st.integers(1, 7 * 24 * 60)),
    ),
)
def test_a_session_any_limit_stopped_reads_limited_until_its_reset(now, limit: tuple[bool, int]):
    """Given a session that the session limit stops at any moment, until any minute within five
    hours, or that the weekly limit stops, until any minute within seven days
    When its end is read at the moment it ended
    Then it is limited until that reset"""
    weekly, minutes = limit
    reset = now.replace(second=0, microsecond=0) + timedelta(minutes=minutes)
    with tempfile.TemporaryDirectory() as folder:
        claude_double.script(
            folder, "Review.", Answer("limited", "so far", now, reset, weekly=weekly)
        )
        arguments = [
            "-p",
            "Review.",
            "--output-format",
            "stream-json",
            "--verbose",
            "--session-id",
            "s",
        ]
        code, out, err, _ = claude_double.answer(arguments, os.getcwd(), folder)

    ended = ending(Output(code, out, err), now)

    assert ended == Limited("so far", "s", reset)
