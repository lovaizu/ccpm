"""The unit cases of session/ending.py, how a Claude Code session's end reads: `ending`, of a
session that answered, beside the rate limit event that each run gives while it's allowed, and with
tools denied on the way; of one that the session limit stops, until later that night, past midnight,
at 12 in the morning and at 12 noon, and that the weekly limit stops days ahead; of one that a
server error ends, and one whose resume finds no session; and of a run that printed nothing, or no
JSON. Each output is as the double of Claude Code gives it from its records."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any

import claude_double
import pytest
from claude_double import Answer, Use, failed, finished, limited
from overnight_bench import RESET, STOPPED, at
from session.claude import Output
from session.ending import Failed, Finished, Limited, ending

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")

SESSION = "1b4e28ba-2fa1-4d3b-a3f5-ef19ae0f1a01"
PROMPT = "Review the payment module."


def output(tmp_path: Any, given: Answer, *more: str) -> Output:
    """What `claude` gives for a run of the prompt in a session of its own ID that ends as the
    answer says, as the double gives it."""
    folder = os.path.join(str(tmp_path), "claude")
    claude_double.script(folder, PROMPT, given)
    arguments = [
        "-p",
        PROMPT,
        "--output-format",
        "stream-json",
        "--verbose",
        "--session-id",
        SESSION,
    ]
    code, out, err, _ = claude_double.answer([*arguments, *more], str(tmp_path), folder)
    return Output(code, out, err)


@pytest.mark.supports(
    "test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit"
)
def test_a_session_that_answered_reads_finished_beside_its_allowed_rate_limit(tmp_path: Any):
    """Given the output of a session that answered, whose stream tells the rate limit that allowed
    its request
    When its end is read
    Then it is finished, with the reply and the session"""
    given = output(tmp_path, finished("payments/card.py:88 retries a declined card."))

    assert '"rate_limit_event"' in given.out
    assert ending(given, STOPPED) == Finished(
        "payments/card.py:88 retries a declined card.", SESSION
    )


@pytest.mark.supports("test_a_task_uses_its_tools_with_no_permission_asked")
def test_a_session_that_answered_with_tools_denied_reads_finished(tmp_path: Any):
    """Given the output of a session that answered after `dontAsk` denied it a shell command
    When its end is read
    Then it is finished, with the reply and the session"""
    use = Use("Bash", None, "touch made-by-the-task")
    given = output(
        tmp_path, finished("I could not make it.", uses=(use,)), "--permission-mode", "dontAsk"
    )

    assert '"permission_denied"' in given.out
    assert ending(given, STOPPED) == Finished("I could not make it.", SESSION)


@pytest.mark.supports(
    "test_a_task_stopped_by_the_limit_goes_on_in_its_session_two_minutes_after_the_reset"
)
@pytest.mark.parametrize(
    ("now", "reset"),
    [
        (STOPPED, RESET),
        (at(23, 50), at(0, 30, 1)),
        (at(23, 10), at(0, 5, 1)),
        (at(11, 20), at(12, 5)),
    ],
    ids=["later that night", "past midnight", "12 in the morning", "12 noon"],
)
def test_a_session_the_session_limit_stopped_reads_limited_until_its_reset(
    tmp_path: Any, now: datetime, reset: datetime
):
    """Given the output of a session that the session limit stopped after part of its reply, until
    a reset later that night, past midnight, at 00:05, or at 12:05
    When its end is read at the moment it ended
    Then it is limited, with the part, the session, and the reset"""
    given = output(tmp_path, limited("## The checks of a card payment", now, reset))

    assert ending(given, now) == Limited("## The checks of a card payment", SESSION, reset)


@pytest.mark.supports(
    "test_a_task_stopped_by_the_limit_goes_on_in_its_session_two_minutes_after_the_reset"
)
def test_a_session_the_weekly_limit_stopped_reads_limited_until_its_reset_days_ahead(tmp_path: Any):
    """Given the output of a session that the weekly limit stopped at 00:41, until 00:00 three days
    on
    When its end is read at 00:41
    Then it is limited, with the reset three days on"""
    reset = at(0, 0, 4)
    given = output(tmp_path, Answer("limited", "so far", STOPPED, reset, weekly=True))

    assert ending(given, STOPPED) == Limited("so far", SESSION, reset)
    assert reset - STOPPED > timedelta(days=2)


@pytest.mark.supports("test_a_failed_session_gives_up_its_task_and_the_others_go_on")
def test_a_session_a_server_error_ended_reads_failed_with_why(tmp_path: Any):
    """Given the output of a session that a server error ended after part of its reply
    When its end is read
    Then it is failed, with the part, the session, and why"""
    given = output(tmp_path, failed("half a review"))

    ended = ending(given, STOPPED)

    assert isinstance(ended, Failed)
    assert (ended.reply, ended.session, bool(ended.why)) == ("half a review", SESSION, True)


@pytest.mark.supports("test_a_carried_on_task_whose_session_is_gone_is_given_up")
def test_a_resume_that_found_no_session_reads_failed_naming_it(tmp_path: Any):
    """Given the output of `claude --resume` of a session that Claude Code doesn't have
    When its end is read
    Then it is failed, with no reply, that session, and why"""
    folder = os.path.join(str(tmp_path), "claude")
    gone = "4e7b5bed-5c23-4a6e-c6c8-1c4d4d3d3d04"
    arguments = ["-p", "Go on.", "--output-format", "stream-json", "--verbose", "--resume", gone]
    code, out, err, _ = claude_double.answer(arguments, str(tmp_path), folder)

    ended = ending(Output(code, out, err), STOPPED)

    assert isinstance(ended, Failed)
    assert (ended.reply, ended.session, bool(ended.why)) == ("", gone, True)


@pytest.mark.supports("test_a_failed_session_gives_up_its_task_and_the_others_go_on")
@pytest.mark.parametrize(
    "given",
    [Output(1, "", "Error: sandbox required but unavailable\n"), Output(0, "not json\n", "")],
    ids=["nothing printed", "no JSON"],
)
def test_a_run_that_printed_no_stream_reads_failed_with_no_session(given: Output):
    """Given a run of `claude` that printed nothing and ended with 1, or printed no JSON and ended
    with 0
    When its end is read
    Then it is failed, with no reply, no session, and why"""
    ended = ending(given, STOPPED)

    assert isinstance(ended, Failed)
    assert (ended.reply, ended.session, bool(ended.why)) == ("", None, True)
