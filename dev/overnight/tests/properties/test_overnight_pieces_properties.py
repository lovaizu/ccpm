"""The property-based tests of pieces, as overnight's Test strategy names them: each invariant that
the architecture states of the records and of how each piece stands, on which the hand-over of a
new piece and the status of a night rest.

- Each piece numbered next after the highest that any earlier record holds (Concept model's
  strategy, S1): the highest of any `.overnight/` is the greatest number of a piece's folder in it,
  whatever else lies beside, else a new piece meets an earlier piece's record.
- Each record written whole at each change (Concept model's strategy, P3.2, P5.1): after any course
  of changes that a runner makes, with any tools and last words, the record read is the one the
  last change gave, else a later session shows another night than the one that ran.
- A piece still recorded as running or waiting after its runner ended counted as stopped (P5.2,
  P5.3): of any night, the share stopped counts exactly those, by the session closing or by the
  usage limit, and never a piece done or failed, else the status misstates the key result."""

from __future__ import annotations

import os
import tempfile
from datetime import date, datetime, timedelta
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from overnight_files import handed
from overnight_inputs import TOOLS, ZONES
from pieces.process import Runner, identify
from pieces.record import Ending, Record, Wait, begin, end, highest, read, resume, wait
from pieces.standing import Night, Standing, Stop, stand

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's bodies aren't built yet")

# Words as Claude Code or the system writes them: any letters, marks, quotes, and newlines.
WORDS = st.text(st.characters(blacklist_categories=("Cs",)), max_size=40)
NUMBERS = st.integers(1, 10**6)
DAYS = st.dates(date(2020, 1, 1), date(2099, 12, 31))
# Any time with a zone, as a runner records the stop and the reset in the machine's zone.
TIMES = st.builds(
    lambda when, zone: when.replace(tzinfo=zone),
    st.datetimes(datetime(2020, 1, 1), datetime(2099, 1, 1)),
    ZONES,
)
WAITS = st.builds(
    lambda began, hours: Wait(began, began + timedelta(hours=hours)), TIMES, st.integers(0, 200)
)
# A name in `.overnight/` that isn't a piece's folder, though it may nearly read as one.
OTHERS = st.one_of(
    st.from_regex(r"[a-z]{1,8}-[0-9]{1,3}", fullmatch=True),
    st.builds(lambda d, n: f"{d:%Y%m%d}-{n}x", DAYS, NUMBERS),
    st.builds(lambda d, n: f"x{d:%Y%m%d}-{n}", DAYS, NUMBERS),
    st.builds(lambda d: f"{d:%Y%m%d}-", DAYS),
)


@pytest.mark.supports(
    "test_a_new_piece_takes_the_number_after_the_highest_of_records_branches_and_worktrees"
)
@given(
    st.lists(st.tuples(DAYS, NUMBERS), max_size=6),
    st.lists(OTHERS, max_size=4),
    st.lists(st.tuples(DAYS, NUMBERS), max_size=2),
)
def test_the_highest_number_is_the_greatest_of_the_pieces_folders(
    pieces: list[tuple[date, int]], others: list[str], files: list[tuple[date, int]]
):
    """Given any `.overnight/` with none, one, or several pieces' folders `<yyyymmdd>-<n>` of any
    days, beside folders of other names that nearly read as one, and files named as one
    When the highest number of its records is asked
    Then it is the greatest number of the pieces' folders, or 0 where there is none
    (Model-based, resting on Concept model's strategy of each piece numbered next, S1.)"""
    with tempfile.TemporaryDirectory() as repo:
        top = os.path.join(repo, ".overnight")
        os.makedirs(top)
        folders = {f"{day:%Y%m%d}-{number}" for day, number in pieces}
        for name in folders | set(others):
            os.makedirs(os.path.join(top, name), exist_ok=True)
        for day, number in files:
            name = f"{day:%Y%m%d}-{number}"
            if name not in folders:
                with open(os.path.join(top, name), "w", encoding="utf-8") as f:
                    f.write("")
        assert highest(repo) == max((number for _, number in pieces), default=0)


@st.composite
def courses(draw: Any) -> list[tuple[str, Any]]:
    """A course of changes that a runner makes to its piece's record: none, one, or several waits,
    each followed by a run again, then a last wait still open, or an end done or failed with any
    words, or neither."""
    course: list[tuple[str, Any]] = []
    for each in draw(st.lists(WAITS, max_size=4)):
        course += [("wait", each), ("resume", None)]
    last = draw(st.sampled_from(["running", "waiting", "done", "failed"]))
    if last == "waiting":
        course.append(("wait", draw(WAITS)))
    elif last in ("done", "failed"):
        course.append((last, draw(WORDS)))
    return course


@pytest.mark.supports("test_a_pieces_wait_is_shown_while_it_waits_and_its_last_words_once_it_ends")
@given(NUMBERS, TOOLS, courses())
def test_each_record_read_is_the_one_its_last_change_gave(
    number: int, tools: tuple[str, ...], course: list[tuple[str, Any]]
):
    """Given any piece, with any tools, recorded as begun, and any course of changes that its
    runner makes: waits at any times, each run again, and an end with any words
    When each change is recorded, and the records are read after each
    Then each change gives the record that the model of the course gives, and each read gives that
    record alone
    (Model-based, resting on Concept model's strategy of each record written whole, P3.2, P5.1.)"""
    with tempfile.TemporaryDirectory() as repo:
        piece = handed(number, tools)
        runner = identify(os.getpid())
        model = Record(piece, "running", runner, (), "")
        assert begin(repo, piece, os.getpid()) == model
        for change, value in course:
            if change == "wait":
                model = Record(piece, "waiting", runner, (*model.waits, value), "")
                given_back = wait(repo, number, value.began, value.resets)
            elif change == "resume":
                model = Record(piece, "running", runner, model.waits, "")
                given_back = resume(repo, number)
            else:
                ending: Ending = "done" if change == "done" else "failed"
                model = Record(piece, ending, runner, model.waits, value)
                given_back = end(repo, number, ending, value)
            assert given_back == model
            assert read(repo) == [model]


@st.composite
def nights(draw: Any) -> list[tuple[Record, bool]]:
    """Any night of none, one, or several pieces, by their numbers, each in any state, with tools
    and words of any kind, each with a runner that runs, or one whose ID now names a later process,
    as an OS tells a runner that ended."""
    own = identify(os.getpid())
    ended = Runner(own.pid, f"{own.started} and later")
    found = []
    for number in sorted(draw(st.sets(NUMBERS, max_size=6))):
        state = draw(st.sampled_from(["running", "waiting", "done", "failed"]))
        runs = draw(st.booleans())
        waits = tuple(draw(st.lists(WAITS, max_size=2)))
        record = Record(
            handed(number, draw(TOOLS)), state, own if runs else ended, waits, draw(WORDS)
        )
        found.append((record, runs))
    return found


@pytest.mark.supports(
    "test_the_share_stopped_counts_neither_a_failed_piece_nor_one_with_a_refused_call"
)
@given(nights())
def test_the_pieces_stopped_are_those_left_running_or_waiting_by_a_runner_that_ended(
    night: list[tuple[Record, bool]],
):
    """Given any night of records in any states, each with a runner that runs or one that ended
    When how each piece stands is asked
    Then each stands in its order, stopped by the session closing where it was running and by the
    usage limit where it was waiting, its runner ended, and by nothing otherwise; and the count
    stopped is the count of those
    (Model-based, resting on P5.2, P5.3, and pieces' strategies of a runner counted ended.)"""
    stops: dict[str, Stop] = {"running": "session closing", "waiting": "usage limit"}
    model = tuple(
        Standing(record, None if runs else stops.get(record.state)) for record, runs in night
    )
    given_back = stand([record for record, _ in night])
    assert given_back == Night(model)
    assert given_back.stopped == sum(each.stopped is not None for each in model)
