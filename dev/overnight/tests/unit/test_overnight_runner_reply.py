"""The unit cases of runner/reply.py, what a reply of Claude Code says: `read`, of a run that ends,
one resumed that ends, one that ends after a call refused on the way, one that ends by an error of
its own, one resumed in no conversation, output that can't be read, and a run that the session
limit, the weekly limit, or a usage limit with no time stops, each reset time on either side of the
clock's time, at midnight, and at noon."""

from __future__ import annotations

import json
from datetime import datetime

import pytest
from claude_code import claude_double
from claude_code.claude_double import MANUAL, RUN
from overnight_stand_ins import NIGHT, ZONE, Clock
from runner.claude import Output
from runner.reply import Ended, Failed, Limited, read

pytestmark = pytest.mark.xfail(strict=True, reason="runner.reply isn't built yet")

# The conversation that each recorded line of a stop names.
STOPPED_IN = "63e0829b-f01b-4bd6-aa0e-c40760caa850"


def output(record: str, event: str, resets: tuple[str, str] | None = None) -> Output:
    """What a run gave, as the record's line of the event holds it, with the stop's reset time
    replaced where `resets` gives the time it holds and the one in its place."""
    given = claude_double.line(record, event)
    stdout = given["stdout"]
    if resets:
        stdout = stdout.replace(*resets)
    return Output(given["exit"], stdout, given["stderr"])


def session_limit(resets: str) -> Output:
    """A run that the session limit stops, which resets at the time, in Claude Code's words."""
    event = "the session limit stops a run, with the time it resets"
    return output(MANUAL, event, (claude_double.SESSION_RESETS, resets))


def weekly_limit(resets: str) -> Output:
    """A run that the weekly limit stops, which resets on the day and time, in Claude Code's
    words."""
    event = "the weekly limit stops a run, with the day and time it resets"
    return output(MANUAL, event, (claude_double.WEEKLY_RESETS, resets))


@pytest.mark.supports(
    "test_the_walkthroughs_three_pieces_go_on_through_the_limit_and_show_done_in_a_later_session"
)
def test_a_run_that_ends_is_ended_in_its_conversation_with_its_last_words(clock: Clock):
    """Given Claude Code's reply of a run that ended with the words `Fixed it.`
    When it's read
    Then it's Ended, in the conversation that the reply names, with those last words"""
    given = output(RUN, "a run ends with its last words")
    assert read(given) == Ended("63e0829b-f01b-4bd6-aa0e-c40760caa850", "Fixed it.")


@pytest.mark.supports(
    "test_a_piece_the_limit_stops_twice_goes_on_in_its_conversation_after_each_reset"
)
def test_a_run_resumed_that_ends_is_ended_with_its_last_words(clock: Clock):
    """Given Claude Code's reply of a run resumed in its conversation, which ended with `Went on.`
    When it's read
    Then it's Ended, in that conversation, with those last words"""
    given = output(RUN, "a run resumed goes on in its conversation and ends")
    assert read(given) == Ended("63e0829b-f01b-4bd6-aa0e-c40760caa850", "Went on.")


@pytest.mark.supports(
    "test_the_share_stopped_counts_neither_a_failed_piece_nor_one_with_a_refused_call"
)
def test_a_run_that_ends_after_a_refused_call_is_ended_by_how_it_ended(clock: Clock):
    """Given Claude Code's reply of a run that ended with `Refused.` after a call to a tool not
    allowed was refused on the way
    When it's read
    Then it's Ended, in the conversation that the reply names, with those last words, not Failed"""
    given = output(RUN, "a run refuses a call to a tool not allowed at once, and ends")
    assert read(given) == Ended("0af6c831-5066-4af5-aa90-1738a0ba4c2e", "Refused.")


@pytest.mark.supports("test_a_piece_ended_by_an_error_of_its_own_is_recorded_failed_with_the_error")
def test_a_run_ended_by_an_error_of_its_own_is_failed_with_claude_codes_words(clock: Clock):
    """Given Claude Code's reply of a run whose turns ran out, an error of its own
    When it's read
    Then it's Failed, with Claude Code's words of the error"""
    given = output(RUN, "a run ends by an error of its own")
    assert read(given) == Failed("Reached maximum number of turns (1)")


@pytest.mark.supports("test_a_piece_ended_by_an_error_of_its_own_is_recorded_failed_with_the_error")
def test_a_run_resumed_in_no_conversation_is_failed_with_claude_codes_words(clock: Clock):
    """Given Claude Code's reply of a run resumed in a conversation that isn't there, which prints
    nothing on its standard output
    When it's read
    Then it's Failed, with the words of its standard error"""
    given = read(output(RUN, "a run resumed in no conversation fails"))
    assert isinstance(given, Failed)
    expected = "No conversation found with session ID: 00000000-0000-0000-0000-000000000000"
    assert given.error.strip() == expected


@pytest.mark.supports("test_a_piece_ended_by_an_error_of_its_own_is_recorded_failed_with_the_error")
@pytest.mark.parametrize(
    "given",
    [Output(0, "Fixed it.\n", ""), Output(1, "{not json", "a crash\n"), Output(0, "[]\n", "")],
    ids=["text in place of JSON", "JSON cut short", "JSON of another form"],
)
def test_output_that_cant_be_read_is_failed_with_words_of_what_was_wrong(
    clock: Clock, given: Output
):
    """Given output of Claude Code that isn't the JSON of a reply: text, JSON cut short, or JSON
    of another form
    When it's read
    Then it's Failed, with words that say what was wrong, so that the piece ends and never waits"""
    read_back = read(given)
    assert isinstance(read_back, Failed)
    assert read_back.error.strip()


@pytest.mark.supports(
    "test_a_piece_the_limit_stops_twice_goes_on_in_its_conversation_after_each_reset"
)
@pytest.mark.parametrize(
    ("resets", "expected"),
    [
        ("11:30pm", datetime(2026, 11, 24, 23, 30, tzinfo=ZONE)),
        ("11:01pm", datetime(2026, 11, 24, 23, 1, tzinfo=ZONE)),
        ("10:59pm", datetime(2026, 11, 25, 22, 59, tzinfo=ZONE)),
        ("3:45pm", datetime(2026, 11, 25, 15, 45, tzinfo=ZONE)),
        ("12:00am", datetime(2026, 11, 25, 0, 0, tzinfo=ZONE)),
        ("12:30pm", datetime(2026, 11, 25, 12, 30, tzinfo=ZONE)),
    ],
    ids=[
        "later tonight",
        "a minute after now",
        "a minute before now, so tomorrow",
        "the page's own, tomorrow",
        "midnight",
        "noon",
    ],
)
def test_a_session_limit_resets_at_its_next_time_after_now(
    clock: Clock, resets: str, expected: datetime
):
    """Given the clock at 23:00 of Tuesday 2026-11-24, east of UTC, and Claude Code's reply that
    the session limit stopped the run, which resets at the time
    When it's read
    Then it's Limited, in the conversation that the reply names, resetting at the first such time
    after now, in the clock's zone"""
    assert clock.at == NIGHT
    assert read(session_limit(resets)) == Limited(STOPPED_IN, expected)


@pytest.mark.supports("test_a_weekly_limit_is_waited_until_its_day_and_time")
@pytest.mark.parametrize(
    ("resets", "expected"),
    [
        ("Mon 12:00am", datetime(2026, 11, 30, 0, 0, tzinfo=ZONE)),
        ("Wed 9:05am", datetime(2026, 11, 25, 9, 5, tzinfo=ZONE)),
        ("Tue 11:30pm", datetime(2026, 11, 24, 23, 30, tzinfo=ZONE)),
        ("Tue 10:00pm", datetime(2026, 12, 1, 22, 0, tzinfo=ZONE)),
    ],
    ids=["the page's own", "tomorrow", "later today", "earlier today, so next week"],
)
def test_a_weekly_limit_resets_at_its_next_day_and_time_after_now(
    clock: Clock, resets: str, expected: datetime
):
    """Given the clock at 23:00 of Tuesday 2026-11-24, east of UTC, and Claude Code's reply that
    the weekly limit stopped the run, which resets on the day and time
    When it's read
    Then it's Limited, in the conversation that the reply names, resetting at the first such day
    and time after now, in the clock's zone"""
    assert read(weekly_limit(resets)) == Limited(STOPPED_IN, expected)


@pytest.mark.supports(
    "test_a_limit_that_gives_no_reset_time_is_waited_a_set_while_and_the_piece_goes_on"
)
def test_a_usage_limit_with_no_time_is_limited_with_no_reset(clock: Clock):
    """Given Claude Code's reply that a usage limit stopped the run, whose words give no time
    When it's read
    Then it's Limited, in the conversation that the reply names, with no reset time"""
    given = output(MANUAL, "a usage limit stops a run, with no time it resets")
    assert read(given) == Limited(STOPPED_IN, None)


@pytest.mark.supports(
    "test_the_walkthroughs_three_pieces_go_on_through_the_limit_and_show_done_in_a_later_session"
)
def test_a_reply_that_names_a_limit_only_in_its_last_words_is_ended(clock: Clock):
    """Given Claude Code's reply of a run that ended, whose last words are about a usage limit
    with a reset time
    When it's read
    Then it's Ended with those words, as the run itself was never stopped"""
    given = claude_double.line(RUN, "a run ends with its last words")
    reply = json.loads(given["stdout"])
    reply["result"] = "Explained the error You've hit your session limit · resets 3:45pm in docs."
    read_back = read(Output(0, json.dumps(reply), ""))
    assert read_back == Ended(reply["session_id"], reply["result"])
