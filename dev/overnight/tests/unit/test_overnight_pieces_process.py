"""The unit cases of pieces/process.py, how the OS tells a runner's process apart: `identify`, of a
process that runs, of one that ended, and of an ID that no process holds; and `runs`, of a runner
that runs, of one that ended, and of one whose ID a process with another start time holds."""

from __future__ import annotations

import os
import subprocess
import sys

import overnight_files
import pytest
from pieces.process import Runner, identify, runs

pytestmark = pytest.mark.xfail(strict=True, reason="pieces.process isn't built yet")

# An ID above what the OSes that Claude Code runs on give a process.
NO_SUCH_ID = 2**31 - 2


@pytest.mark.supports(
    "test_a_piece_whose_runner_ended_while_it_ran_is_shown_stopped_by_the_session_closing"
)
def test_identify_of_a_process_that_runs_gives_its_id_and_start_time_the_same_each_time():
    """Given this process, which runs
    When it's identified twice
    Then each gives its ID, with a start time that isn't blank, the same both times"""
    first, second = identify(os.getpid()), identify(os.getpid())
    assert first == second
    assert first.pid == os.getpid()
    assert first.started.strip()


@pytest.mark.supports(
    "test_a_piece_whose_runner_ended_while_it_ran_is_shown_stopped_by_the_session_closing"
)
def test_identify_tells_two_processes_apart_by_their_start_times():
    """Given this process and a child of it that runs
    When each is identified
    Then each gives its own ID, and the two differ"""
    child = overnight_files.running_process()
    try:
        assert identify(child.pid) != identify(os.getpid())
        assert identify(child.pid).pid == child.pid
    finally:
        overnight_files.shut_down(child)


@pytest.mark.supports(
    "test_a_piece_whose_runner_ended_while_it_ran_is_shown_stopped_by_the_session_closing"
)
@pytest.mark.parametrize(
    "pid",
    [overnight_files.ended_process, lambda: NO_SUCH_ID],
    ids=["a process that ended", "an ID no process holds"],
)
def test_identify_of_an_id_that_no_process_runs_by_is_refused_naming_it(pid):
    """Given the ID of a process that ended, or one that no process holds
    When it's identified
    Then LookupError is raised, naming the ID"""
    given = pid()
    with pytest.raises(LookupError, match=str(given)):
        identify(given)


@pytest.mark.supports(
    "test_a_piece_whose_runner_ended_while_it_ran_is_shown_stopped_by_the_session_closing"
)
def test_runs_of_a_runner_that_runs_is_true():
    """Given this process, as identify gives it
    When whether it runs is asked
    Then it is True"""
    assert runs(identify(os.getpid())) is True


@pytest.mark.supports(
    "test_a_piece_whose_runner_ended_while_it_ran_is_shown_stopped_by_the_session_closing"
)
def test_runs_of_a_runner_that_ended_is_false():
    """Given a child process as identify gave it, which then ended
    When whether it runs is asked
    Then it is False"""
    child = subprocess.Popen(
        [sys.executable, "-c", "import sys; sys.stdin.read()"], stdin=subprocess.PIPE
    )
    runner = identify(child.pid)
    child.communicate(b"")
    assert runs(runner) is False


@pytest.mark.supports(
    "test_a_piece_whose_runner_ended_while_it_ran_is_shown_stopped_by_the_session_closing"
)
def test_runs_of_a_runner_whose_id_now_names_a_later_process_is_false():
    """Given a runner of this process's ID with a start time other than its own, as when the ID
    now names a later process
    When whether it runs is asked
    Then it is False"""
    own = identify(os.getpid())
    assert runs(Runner(own.pid, f"{own.started} and later")) is False
