"""The unit cases of pieces/standing.py, how each piece stands: `stand`, of no record, of a record
of each state with its runner running and ended, and of several in their order; and
`Night.stopped`, of none, one, and several pieces stopped among others."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone

import pytest
from pieces.record import Handed, Record, begin, end, read, wait
from pieces.standing import Night, Standing, stand

pytestmark = pytest.mark.xfail(strict=True, reason="pieces.standing isn't built yet")

ZONE = timezone(timedelta(hours=9))
STOP = datetime(2026, 11, 25, 1, 12, tzinfo=ZONE)
RESET = datetime(2026, 11, 25, 4, 0, tzinfo=ZONE)


@pytest.fixture
def child() -> Iterator[subprocess.Popen]:
    """A child process that runs until the case ends it."""
    started = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    yield started
    started.kill()
    started.wait()


def recorded(repo: str, number: int, state: str, pid: int) -> None:
    """Records piece of the number in the state, carried by the process of the ID."""
    begin(repo, Handed(number, f"../myapp-overnight-{number}", f"overnight/{number}", ("Read",)), pid)
    if state == "waiting":
        wait(repo, number, STOP, RESET)
    elif state in ("done", "failed"):
        end(repo, number, state, "Done." if state == "done" else "an error")


def ended(child: subprocess.Popen) -> None:
    """Ends the child process, as the OS shuts a runner down."""
    child.kill()
    child.wait()


@pytest.mark.supports("test_status_with_no_piece_handed_over_shows_no_pieces_yet")
def test_stand_of_no_record_is_a_night_of_none_with_none_stopped():
    """Given no record
    When how each piece stands is asked
    Then it is a night of no standing, with 0 stopped"""
    night = stand([])
    assert night == Night(())
    assert night.stopped == 0


@pytest.mark.supports(
    "test_the_walkthroughs_three_pieces_go_on_through_the_limit_and_show_done_in_a_later_session"
)
@pytest.mark.parametrize("state", ["running", "waiting"])
def test_a_piece_running_or_waiting_whose_runner_runs_is_stopped_by_nothing(repo: str, state):
    """Given piece 1 recorded running, or waiting, and carried by this process, which runs
    When how it stands is asked
    Then it stands as its record says, stopped by nothing, and 0 are stopped"""
    recorded(repo, 1, state, os.getpid())
    records = read(repo)
    night = stand(records)
    assert night == Night((Standing(records[0], None),))
    assert night.stopped == 0


@pytest.mark.supports(
    "test_a_piece_whose_runner_ended_while_it_ran_is_shown_stopped_by_the_session_closing"
)
def test_a_piece_running_whose_runner_ended_is_stopped_by_the_session_closing(repo: str, child):
    """Given piece 1 recorded running, whose runner then ended
    When how it stands is asked
    Then it stands stopped by the session closing, and 1 is stopped"""
    recorded(repo, 1, "running", child.pid)
    ended(child)
    records = read(repo)
    night = stand(records)
    assert night == Night((Standing(records[0], "session closing"),))
    assert night.stopped == 1


@pytest.mark.supports(
    "test_a_piece_whose_runner_ended_while_it_waited_is_counted_stopped_by_the_usage_limit"
)
def test_a_piece_waiting_whose_runner_ended_is_stopped_by_the_usage_limit(repo: str, child):
    """Given piece 1 recorded waiting, whose runner then ended
    When how it stands is asked
    Then it stands stopped by the usage limit, and 1 is stopped"""
    recorded(repo, 1, "waiting", child.pid)
    ended(child)
    records = read(repo)
    night = stand(records)
    assert night == Night((Standing(records[0], "usage limit"),))
    assert night.stopped == 1


@pytest.mark.supports(
    "test_the_share_stopped_counts_neither_a_failed_piece_nor_one_with_a_refused_call"
)
@pytest.mark.parametrize("state", ["done", "failed"])
def test_a_piece_done_or_failed_whose_runner_ended_is_stopped_by_nothing(repo: str, child, state):
    """Given piece 1 recorded done, or failed, whose runner then ended, as each runner does once
    its conversation ends
    When how it stands is asked
    Then it stands as its record says, stopped by nothing, and 0 are stopped"""
    recorded(repo, 1, state, child.pid)
    ended(child)
    records = read(repo)
    night = stand(records)
    assert night == Night((Standing(records[0], None),))
    assert night.stopped == 0


@pytest.mark.supports(
    "test_the_share_stopped_counts_neither_a_failed_piece_nor_one_with_a_refused_call"
)
def test_several_pieces_stand_in_their_order_with_each_stopped_counted(repo: str, child):
    """Given pieces 1 done, 2 running and 3 waiting whose runner ended, 4 failed, and 10 running
    whose runner runs
    When how they stand is asked
    Then they stand in the order of their records, 2 by the session closing and 3 by the usage
    limit, and 2 are stopped"""
    for number, state in ((1, "done"), (2, "running"), (3, "waiting"), (4, "failed")):
        recorded(repo, number, state, child.pid)
    recorded(repo, 10, "running", os.getpid())
    ended(child)
    records: list[Record] = read(repo)
    night = stand(records)
    stops = (None, "session closing", "usage limit", None, None)
    assert night == Night(tuple(Standing(r, s) for r, s in zip(records, stops)))
    assert night.stopped == 2
