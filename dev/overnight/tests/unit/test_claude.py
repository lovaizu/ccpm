"""The unit cases of how overnight reads what a run of `claude` gave: whether the run is done, the
session it ran in, and why it stopped, which the cases of one work in test_work.py rest on."""

from __future__ import annotations

import subprocess

from double.claude_double import (
    DONE,
    KILLED,
    NO_CONVERSATION,
    RATE_LIMIT,
    REFUSED,
    given,
    result_of,
    session_of,
)
from overnight import claude


def _read(event: str) -> claude.Read:
    return claude.read(subprocess.CompletedProcess([], *given(event)))


def test_a_run_that_exits_0_with_no_error_is_done():
    """Given a run of `claude` that exits 0, and whose result says `is_error` false
    When overnight reads what it gave
    Then the run is done, in the session that its result names"""
    assert _read(DONE) == claude.Read(True, session_of(DONE), result_of(DONE))


def test_a_run_that_exits_0_with_an_error_stopped():
    """Given a run that the rate limit stops, which exits 0 and whose result says `is_error` true
    When overnight reads what it gave
    Then the run stopped, in the session that its result names, for the reason its result says"""
    assert _read(RATE_LIMIT) == claude.Read(False, session_of(RATE_LIMIT), result_of(RATE_LIMIT))


def test_a_run_that_exits_1_with_a_result_stopped():
    """Given a run that the API refuses, which exits 1 with a result
    When overnight reads what it gave
    Then the run stopped, in the session that its result names, for the reason its result says"""
    assert _read(REFUSED) == claude.Read(False, session_of(REFUSED), result_of(REFUSED))


def test_a_run_that_gives_no_result_stopped_for_what_it_said_on_stderr():
    """Given a resume that finds no conversation, which exits 1 with no result and a line on stderr
    When overnight reads what it gave
    Then the run stopped, in no session it names, for the reason that stderr says"""
    assert _read(NO_CONVERSATION) == claude.Read(
        False, None, "No conversation found with session ID: 11111111-1111-1111-1111-111111111111"
    )


def test_a_run_that_says_nothing_stopped_for_its_exit_code():
    """Given a run that is killed, which gives exit code -9 and nothing on stdout or stderr
    When overnight reads what it gave
    Then the run stopped, in no session it names, for its exit code"""
    assert _read(KILLED) == claude.Read(False, None, "exit code -9")
