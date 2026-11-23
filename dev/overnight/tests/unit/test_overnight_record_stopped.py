"""The unit cases of record/stopped.py, what a run becomes once its runner stopped: `left`, of a run
in each of the five states, and `carried_on`, of a finished run, of one given up with stops and a
session, and of one given up before it started."""

from __future__ import annotations

import pytest
from overnight_bench import PAYMENTS_ENDED, RESET, STOPPED, WENT_ON, at
from record.runs import Run, Wait
from record.stopped import carried_on, left

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")

SEEN = at(7, 0, 1)


def given_up_at_the_stop(run: Run, given: Run) -> None:
    """Asserts that the run is the one given, given up at the moment the stop was seen, with why."""
    assert (given.state, given.ended) == ("given up", SEEN)
    assert given.why
    assert (given.session, given.stops, given.waits, given.until) == (
        run.session,
        run.stops,
        run.waits,
        None,
    )


@pytest.mark.supports("test_a_task_left_unended_by_a_stop_ends_given_up_with_that_reason")
def test_a_run_waiting_for_the_start_is_given_up_with_why():
    """Given a run waiting for the start, with no session
    When its runner's stop is seen at 07:00
    Then it is given up at 07:00 with why, still with no session"""
    run = Run("waiting for the start", None, 0, (), None, None, None)

    given_up_at_the_stop(run, left(run, SEEN))


@pytest.mark.supports("test_a_task_left_unended_by_a_stop_ends_given_up_with_that_reason")
def test_a_running_run_is_given_up_with_why_and_its_session():
    """Given a run running in its session, stopped once before
    When its runner's stop is seen at 07:00
    Then it is given up at 07:00 with why, its session, its stop, and its wait"""
    run = Run("running", "s", 1, (Wait(STOPPED, WENT_ON),), None, None, None)

    given_up_at_the_stop(run, left(run, SEEN))


@pytest.mark.supports("test_a_task_left_unended_by_a_stop_ends_given_up_with_that_reason")
def test_a_run_waiting_for_the_limit_is_given_up_and_no_longer_waits():
    """Given a run waiting for the limit until 01:42, in its session
    When its runner's stop is seen at 07:00
    Then it is given up at 07:00 with why and its session, with no moment it goes on"""
    run = Run("waiting for the limit", "s", 1, (Wait(STOPPED, None),), RESET, None, None)

    given_up_at_the_stop(run, left(run, SEEN))


@pytest.mark.supports("test_a_task_left_unended_by_a_stop_ends_given_up_with_that_reason")
@pytest.mark.parametrize(
    "run",
    [
        Run("finished", "s", 1, (Wait(STOPPED, WENT_ON),), None, PAYMENTS_ENDED, None),
        Run("given up", "s", 7, (), None, PAYMENTS_ENDED, "the usage limit stopped it 7 times"),
    ],
    ids=["finished", "given up"],
)
def test_a_run_that_ended_is_left_as_it_was(run: Run):
    """Given a run finished, or given up with why
    When its runner's stop is seen at 07:00
    Then it is the run as it was"""
    assert left(run, SEEN) == run


@pytest.mark.supports("test_stacking_again_carries_on_each_unfinished_task_in_its_session")
def test_a_finished_run_carried_on_is_left_as_it_ended():
    """Given a finished run
    When its queue is stacked again
    Then it is the run as it was"""
    run = Run("finished", "s", 1, (Wait(STOPPED, WENT_ON),), None, PAYMENTS_ENDED, None)

    assert carried_on(run) == run


@pytest.mark.supports(
    "test_stacking_again_carries_on_each_unfinished_task_in_its_session",
    "test_a_carried_on_task_counts_its_stops_at_the_limit_from_zero",
)
def test_a_given_up_run_carried_on_waits_for_the_start_in_its_session_with_no_stops():
    """Given a run given up with why in its session, after six stops
    When its queue is stacked again
    Then it waits for the start in the same session, with no stops, none of its earlier waits, no
    end, no why, and no moment it goes on"""
    run = Run("given up", "s", 6, (Wait(STOPPED, WENT_ON),), None, PAYMENTS_ENDED, "stopped")

    assert carried_on(run) == Run("waiting for the start", "s", 0, (), None, None, None)


@pytest.mark.supports("test_stacking_again_carries_on_each_unfinished_task_in_its_session")
def test_a_run_given_up_before_it_started_carried_on_waits_for_the_start_anew():
    """Given a run given up with why before it started, with no session
    When its queue is stacked again
    Then it waits for the start, with no session"""
    given = carried_on(Run("given up", None, 0, (), None, SEEN, "overnight stopped"))

    assert given == Run("waiting for the start", None, 0, (), None, None, None)
