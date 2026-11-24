"""The unit cases of runner/carry.py, how a piece is carried to its end: `carry`, of a run that ends
at once, after a call refused on the way, or by an error of its own; of none, one, and several stops
of the usage limit before it ends, each with its reset time, a weekly one, and one with no time;
and where `claude` can't be found."""

from __future__ import annotations

import os
from datetime import datetime

import overnight_stand_ins
import pytest
from claude_code import claude_double
from overnight_stand_ins import NIGHT, ZONE, Clock, handed_over
from pieces.process import identify
from pieces.record import Handed, Record, State, Wait, read
from runner.carry import carry

pytestmark = pytest.mark.xfail(strict=True, reason="runner.carry isn't built yet")


def ended(handed: Handed, state: State, waits: tuple[Wait, ...], last_words: str) -> Record:
    """The record of the piece once carried, as `end` writes it."""
    return Record(handed, state, identify(os.getpid()), waits, last_words)


def resumes(stand_in: str) -> list[str | None]:
    """The conversation that each run of the piece resumed, None for a run anew."""
    return [each["resume"] for each in claude_double.calls(stand_in)]


@pytest.mark.supports(
    "test_the_walkthroughs_three_pieces_go_on_through_the_limit_and_show_done_in_a_later_session"
)
def test_a_piece_that_ends_at_once_is_recorded_done_with_its_last_words(
    repo: str, stand_in: str, clock: Clock
):
    """Given the walkthrough's piece recorded running, and Claude Code ending its run with its
    last words
    When it's carried
    Then Claude Code ran once, anew; no wait was made; and the record is done with no wait and
    those last words"""
    piece, handed = handed_over(repo)
    words = "Fixed parse_date for leap days. 214 tests pass."
    claude_double.plays(stand_in, {"1": [{"kind": "ends", "last_words": words}]})
    carry(piece)
    assert resumes(stand_in) == [None]
    assert clock.waits == []
    assert read(repo) == [ended(handed, "done", (), words)]


@pytest.mark.supports(
    "test_a_call_to_a_tool_not_named_is_refused_at_once_and_the_piece_goes_on_to_its_end"
)
def test_a_piece_whose_run_had_a_call_refused_is_recorded_done(
    repo: str, stand_in: str, clock: Clock
):
    """Given the walkthrough's piece recorded running, and Claude Code refusing a call to a tool
    not named on the way, then ending with `Refused.`
    When it's carried
    Then Claude Code ran once, and the record is done with no wait and `Refused.`"""
    piece, handed = handed_over(repo)
    claude_double.plays(stand_in, {"1": [{"kind": "refuses", "last_words": "Refused."}]})
    carry(piece)
    assert resumes(stand_in) == [None]
    assert read(repo) == [ended(handed, "done", (), "Refused.")]


@pytest.mark.supports("test_a_piece_ended_by_an_error_of_its_own_is_recorded_failed_with_the_error")
def test_a_piece_ended_by_an_error_of_its_own_is_recorded_failed_and_not_run_again(
    repo: str, stand_in: str, clock: Clock
):
    """Given the walkthrough's piece recorded running, and Claude Code ending its run by an error
    of its own, its turns run out
    When it's carried
    Then Claude Code ran once, no wait was made, and the record is failed with Claude Code's words
    of the error"""
    piece, handed = handed_over(repo)
    claude_double.plays(stand_in, {"1": [{"kind": "errs"}]})
    carry(piece)
    assert resumes(stand_in) == [None]
    assert clock.waits == []
    assert read(repo) == [ended(handed, "failed", (), "Reached maximum number of turns (1)")]


@pytest.mark.supports("test_a_pieces_wait_is_shown_while_it_waits_and_its_last_words_once_it_ends")
def test_a_piece_the_limit_stops_once_waits_until_the_reset_and_goes_on_in_its_conversation(
    repo: str, stand_in: str, clock: Clock
):
    """Given the walkthrough's piece recorded running, and Claude Code stopping it at 23:00 by the
    session limit, which resets at 11:30pm, before it ends with `Done.`
    When it's carried
    Then the runner waited once, until 23:30; Claude Code ran anew and then in the conversation
    of the piece's folder; and the record is done with its wait from 23:00 to 23:30"""
    piece, handed = handed_over(repo)
    claude_double.plays(
        stand_in,
        {
            "1": [
                {"kind": "session limit", "resets": "11:30pm"},
                {"kind": "ends", "last_words": "Done."},
            ]
        },
    )
    carry(piece)
    reset = datetime(2026, 11, 24, 23, 30, tzinfo=ZONE)
    assert clock.waits == [reset]
    assert resumes(stand_in) == [None, claude_double.conversation(piece.folder)]
    assert read(repo) == [ended(handed, "done", (Wait(NIGHT, reset),), "Done.")]


@pytest.mark.supports(
    "test_a_piece_the_limit_stops_twice_goes_on_in_its_conversation_after_each_reset"
)
def test_a_piece_the_limit_stops_three_times_waits_each_and_keeps_each_wait_in_order(
    repo: str, stand_in: str, clock: Clock
):
    """Given the walkthrough's piece recorded running, and Claude Code stopping it by the session
    limit at 23:00, resetting at 11:10pm, then at 23:10, resetting at 11:20pm, then at 23:20,
    resetting at 11:40pm, before it ends with `Done.`
    When it's carried
    Then the runner waited until 23:10, 23:20, and 23:40; each run after the first resumed the
    piece's conversation; and the record is done with the three waits, the earliest first"""
    piece, handed = handed_over(repo)
    stops = [
        {"kind": "session limit", "resets": each} for each in ("11:10pm", "11:20pm", "11:40pm")
    ]
    claude_double.plays(stand_in, {"1": [*stops, {"kind": "ends", "last_words": "Done."}]})
    carry(piece)
    times = [datetime(2026, 11, 24, 23, m, tzinfo=ZONE) for m in (0, 10, 20, 40)]
    assert clock.waits == times[1:]
    assert resumes(stand_in) == [None, *[claude_double.conversation(piece.folder)] * 3]
    waits = tuple(Wait(began, resets) for began, resets in zip(times, times[1:]))
    assert read(repo) == [ended(handed, "done", waits, "Done.")]


@pytest.mark.supports("test_a_weekly_limit_is_waited_until_its_day_and_time")
def test_a_piece_the_weekly_limit_stops_waits_until_its_day_and_time(
    repo: str, stand_in: str, clock: Clock
):
    """Given the walkthrough's piece recorded running, and Claude Code stopping it at 23:00 of
    Tuesday by the weekly limit, which resets on Mon 12:00am, before it ends with `Done.`
    When it's carried
    Then the runner waited once, until 00:00 of Monday 2026-11-30, and the record is done with
    that wait"""
    piece, handed = handed_over(repo)
    claude_double.plays(
        stand_in, {"1": [{"kind": "weekly limit"}, {"kind": "ends", "last_words": "Done."}]}
    )
    carry(piece)
    reset = datetime(2026, 11, 30, 0, 0, tzinfo=ZONE)
    assert clock.waits == [reset]
    assert read(repo) == [ended(handed, "done", (Wait(NIGHT, reset),), "Done.")]


@pytest.mark.supports(
    "test_a_limit_that_gives_no_reset_time_is_waited_a_set_while_and_the_piece_goes_on"
)
def test_a_piece_a_limit_with_no_time_stops_waits_a_set_while_and_goes_on(
    repo: str, stand_in: str, clock: Clock
):
    """Given the walkthrough's piece recorded running, and Claude Code stopping it at 23:00 by a
    usage limit whose words give no time, before it ends with `Done.`
    When it's carried
    Then the runner waited once, until a time after 23:00; the second run resumed the piece's
    conversation; and the record is done with its wait from 23:00 to that time"""
    piece, handed = handed_over(repo)
    claude_double.plays(
        stand_in, {"1": [{"kind": "limit with no time"}, {"kind": "ends", "last_words": "Done."}]}
    )
    carry(piece)
    (until,) = clock.waits
    assert until > NIGHT
    assert resumes(stand_in) == [None, claude_double.conversation(piece.folder)]
    assert read(repo) == [ended(handed, "done", (Wait(NIGHT, until),), "Done.")]


@pytest.mark.supports(
    "test_a_piece_whose_claude_code_cant_start_is_recorded_failed_with_the_systems_words"
)
def test_a_piece_whose_claude_isnt_found_is_recorded_failed_with_the_systems_words(
    repo: str, clock: Clock, monkeypatch: pytest.MonkeyPatch
):
    """Given the walkthrough's piece recorded running, and a PATH on which no `claude` is found
    When it's carried
    Then no wait was made, and the record is failed, with the system's words as its last words"""
    piece, handed = handed_over(repo)
    overnight_stand_ins.path_without_claude(monkeypatch)
    carry(piece)
    assert clock.waits == []
    (record,) = read(repo)
    assert (record.handed, record.state, record.waits) == (handed, "failed", ())
    assert record.last_words.strip()
