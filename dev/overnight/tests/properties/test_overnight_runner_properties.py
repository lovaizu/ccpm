"""The property-based tests of the runner, as overnight's Test strategy names them: each invariant
that the architecture states of how a piece is run and carried through the usage limit, on which
every piece of a night rests.

- The prompt handed to Claude Code on its standard input, with only the named tools allowed and no
  one to ask (Deployment's strategy, P2.1, P2.2): for any prompt and any tools that the user
  writes, Claude Code takes the prompt whole and allows exactly those tools, else a piece works on
  other words than its user's, or a call waits on a prompt that no one answers.
- The reset time read from the stop's reply, or a set while where none can be read (P1.1): for
  any time of the clock and any time or day that the stop gives, the piece waits until the first
  such moment after now, and an unreadable reset never ends the piece, else it waits a day longer
  than the limit holds it, or it stops for good.
- A piece that the usage limit stops goes on in its conversation at each reset, however often it
  stops (P1.1): for any course of stops before the conversation ends, the piece is resumed in its
  conversation after each, with each wait recorded in order, and its end recorded as it ended,
  else the work stops at the limit."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timedelta
from typing import Any

import pytest
from claude_code import claude_double
from claude_code.claude_double import MANUAL
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st
from overnight_files import PROMPT, handed, piece_folder
from overnight_inputs import TOOLS, ZONES
from overnight_stand_ins import Clock
from pieces.record import Wait, begin, read
from runner.carry import Piece, carry
from runner.claude import Output, run
from runner.reply import Limited
from runner.reply import read as read_reply

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's bodies aren't built yet")

# Each input sets the clock and the stand-in's plays anew, so the case's fixtures serve each.
EACH_INPUT = settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
# A property whose each input runs the stand-in, a process for each run, tries fewer inputs.
FEW = settings(EACH_INPUT, max_examples=15)
# A prompt as an AI writes it: any letters, marks, quotes, and newlines, a leading `-` among them,
# but a carriage return, which a reader of text in its standard input turns into a newline.
PROMPTS = st.text(
    st.characters(blacklist_categories=("Cs",), blacklist_characters="\r\x00"), min_size=1
).filter(lambda prompt: prompt.strip() != "")
NOWS = st.builds(
    lambda when, zone: when.replace(second=0, microsecond=0, tzinfo=zone),
    st.datetimes(datetime(2026, 1, 1), datetime(2030, 1, 1)),
    ZONES,
)
DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
# A time of day as Claude Code's page writes a reset: `3:45pm`, `12:00am`.
CLOCK_TIMES = st.tuples(st.integers(1, 12), st.integers(0, 59), st.sampled_from(["am", "pm"]))


def hour_of(hour: int, half: str) -> int:
    """The hour of the day, 0 to 23, of a time of a 12-hour clock."""
    return hour % 12 + (12 if half == "pm" else 0)


def stopped(event: str, words: tuple[str, str]) -> Output:
    """The reply of the record's stop of the event, its reset words replaced."""
    line = claude_double.line(MANUAL, event)
    return Output(line["exit"], line["stdout"].replace(*words), line["stderr"])


def next_after(now: datetime, hour: int, minute: int, weekday: int | None) -> datetime:
    """The first moment after now, in now's zone, at the hour and minute, and on the weekday
    where one is given: the model of a reset."""
    at = now.replace(hour=hour, minute=minute)
    while at <= now or (weekday is not None and at.weekday() != weekday):
        at += timedelta(days=1)
    return at


@pytest.mark.supports("test_the_prompt_reaches_claude_code_whole_on_its_standard_input")
@FEW
@given(PROMPTS, TOOLS)
def test_claude_code_takes_any_prompt_whole_and_allows_exactly_its_tools(
    stand_in: str, prompt: str, tools: tuple[str, ...]
):
    """Given any prompt that an AI writes, a leading option, quotes, and newlines among them, and
    any tools that the user names, rules with spaces, commas, and quotes inside among them
    When Claude Code is run for a piece with them
    Then its one run takes the prompt on its standard input as written, in the mode that asks no
    one, allowing exactly those tools
    (A postcondition, resting on Deployment's strategy of the prompt on standard input, P2.1, and
    on Components' strategy of only the named tools allowed, P2.2.)"""
    with tempfile.TemporaryDirectory() as work:
        folder = piece_folder(os.path.join(work, "myapp"), 1)
        os.makedirs(folder)
        claude_double.plays(stand_in, {"*": [{"kind": "ends"}]})
        run(Piece(work, 1, folder, prompt, tools), None)
        (call,) = [
            each
            for each in claude_double.calls(stand_in)
            if each["cwd"] == os.path.realpath(folder)
        ]
        assert (call["stdin"], call["mode"], call["tools"]) == (prompt, "dontAsk", list(tools))


@pytest.mark.supports("test_a_weekly_limit_is_waited_until_its_day_and_time")
@EACH_INPUT
@given(NOWS, CLOCK_TIMES, st.none() | st.integers(0, 6))
def test_a_stop_resets_at_the_first_moment_after_now_that_its_words_give(
    clock: Clock, now: datetime, time_of_day: tuple[int, int, str], weekday: int | None
):
    """Given the clock at any time, in any zone, and Claude Code's reply that the session limit
    stopped the run, which resets at any time of day, or that the weekly limit did, which resets
    on any day and time
    When the reply is read
    Then it's Limited, resetting at the first such moment after now, in the clock's zone
    (Model-based, resting on P1.1 and Components' strategy of the reset time read from the
    stop's reply.)"""
    hour, minute, half = time_of_day
    assume((hour_of(hour, half), minute) != (now.hour, now.minute))
    clock.at = now
    words = f"{hour}:{minute:02d}{half}"
    if weekday is None:
        event = "the session limit stops a run, with the time it resets"
        given_back = read_reply(stopped(event, (claude_double.SESSION_RESETS, words)))
    else:
        event = "the weekly limit stops a run, with the day and time it resets"
        given_back = read_reply(
            stopped(event, (claude_double.WEEKLY_RESETS, f"{DAYS[weekday]} {words}"))
        )
    assert isinstance(given_back, Limited)
    assert given_back.resets == next_after(now, hour_of(hour, half), minute, weekday)
    assert given_back.resets is not None and given_back.resets.utcoffset() == now.utcoffset()


@pytest.mark.supports(
    "test_a_limit_that_gives_no_reset_time_is_waited_a_set_while_and_the_piece_goes_on"
)
@EACH_INPUT
@given(NOWS, st.text(st.characters(blacklist_categories=("Cs",)), max_size=20))
def test_a_stop_whose_reset_words_cant_be_read_is_still_a_stop(
    clock: Clock, now: datetime, words: str
):
    """Given the clock at any time, and Claude Code's reply that the session limit stopped the run,
    with any words in place of its reset time
    When the reply is read
    Then it's Limited, in the conversation that the reply names, never Failed or Ended
    (An invariant, resting on Components' strategy that an unreadable reply never ends a piece,
    P1.1.)"""
    clock.at = now
    event = "the session limit stops a run, with the time it resets"
    reply = stopped(event, (claude_double.SESSION_RESETS, words))
    given_back = read_reply(reply)
    assert isinstance(given_back, Limited)
    assert given_back.conversation == json.loads(reply.stdout)["session_id"]


STOPS = st.one_of(
    st.builds(
        lambda t: {"kind": "session limit", "resets": f"{t[0]}:{t[1]:02d}{t[2]}"}, CLOCK_TIMES
    ),
    st.builds(
        lambda d, t: {"kind": "weekly limit", "resets": f"{d} {t[0]}:{t[1]:02d}{t[2]}"},
        st.sampled_from(DAYS),
        CLOCK_TIMES,
    ),
    st.just({"kind": "limit with no time"}),
)
ENDS = st.sampled_from([("ends", "done"), ("refuses", "done"), ("errs", "failed")])


@pytest.mark.supports(
    "test_a_piece_the_limit_stops_twice_goes_on_in_its_conversation_after_each_reset"
)
@FEW
@given(NOWS, st.lists(STOPS, max_size=4), ENDS)
def test_a_piece_goes_on_in_its_conversation_after_each_stop_however_often_it_stops(
    clock: Clock,
    stand_in: str,
    now: datetime,
    stops: list[dict[str, Any]],
    ending: tuple[str, str],
):
    """Given the clock at any time, and a piece recorded running that Claude Code stops any number
    of times, by the session limit, the weekly limit, or a limit with no time, before its
    conversation ends, after a refused call, or by an error of its own
    When it's carried
    Then Claude Code ran once for each stop and once more, each run after the first in the
    conversation of the piece's folder; the runner waited once for each stop, each until no
    earlier than it; and the record keeps each wait in order, from the time of its stop to the
    time waited until, and is done, or failed where the run ended by an error of its own
    (Model-based, resting on P1.1, P5.1, and Components' strategy of the conversation's ID kept
    from its first reply.)"""
    kind, state = ending
    clock.at, clock.waits = now, []
    with tempfile.TemporaryDirectory() as work:
        repo = os.path.join(work, "myapp")
        folder = piece_folder(repo, 1)
        os.makedirs(repo)
        os.makedirs(folder)
        begin(repo, handed(1, ("Read",)), os.getpid())
        claude_double.plays(stand_in, {"*": [*stops, {"kind": kind}]})
        carry(Piece(repo, 1, folder, PROMPT, ("Read",)))
        runs = [
            each["resume"]
            for each in claude_double.calls(stand_in)
            if each["cwd"] == os.path.realpath(folder)
        ]
        assert runs == [None, *[claude_double.conversation(folder)] * len(stops)]
        stops_at = [now, *clock.waits[:-1]] if clock.waits else []
        assert all(until >= began for began, until in zip(stops_at, clock.waits))
        (record,) = read(repo)
        expected = tuple(Wait(began, until) for began, until in zip(stops_at, clock.waits))
        assert (record.state, record.waits, len(clock.waits)) == (state, expected, len(stops))
