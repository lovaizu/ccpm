"""The state transition cases of runs.py's `stand`: each state that a role's Start and a Run can be
in, as the run record's lines bring it about, with each line that can come next, a line that the
state doesn't expect included, and the state each leaves: which Starts have ended, the moves due,
the Results the role may give, and the Start that a Mark lies on."""

from __future__ import annotations

from typing import NamedTuple

import lane_data as d
import pytest
import start_states as st
from form import Move
from run_record import (
    Ended,
    Gave,
    Line,
    Marked,
    Prompted,
    Started,
    TextFailed,
    TextGiven,
    Tied,
)
from runs import may_give, stand

# The Routes of the cases of a Start, with a Route after the person's pause.
ROUTES = (
    *st.ROUTES,
    d.route(d.After("command", command="pause"), Move("no_more", result="paused")),
)
START_WRITER = (Move("start", role="writer"),)
START_REVIEWER = (Move("start", role="reviewer"),)
WRITTEN = ("written",)
CALLED = st.CALLED
GAVE = st.GAVE
UNTIED, RUNNING, GAVE_RUNNING = st.UNTIED, st.RUNNING, st.GAVE_RUNNING
ENDED_BARE, ENDED_GAVE = st.ENDED_BARE, st.ENDED_GAVE
RESUMED_BEFORE_END, RESUMED_AFTER_END, RESUMED_OPENED = (
    st.RESUMED_BEFORE_END,
    st.RESUMED_AFTER_END,
    st.RESUMED_OPENED,
)

# Each line that can reach writer's Start, as one event.
TIE = (st.TIED,)
MARK = (Marked("r1", "writer", 1, None, "a01"),)
GIVE = (GAVE,)
END_OF_FIRST = (st.END_FIRST,)
END_NAMING_NONE = (Ended("r1", "a01", False),)
END_KILLED = (Ended("r1", "a01", True),)
END_OF_RESUME = (Ended("r1", "a01", False, "toolu_w2"),)
END_OF_ANOTHER = (Ended("r1", "a99", False, "toolu_x"),)
RESUME_AGAIN = (
    Started("r1", "writer", "And more", {}, "toolu_w3", True, False),
    Tied("r1", "toolu_w3", "a01"),
)


class Stands(NamedTuple):
    """What the state leaves: whether each Start has ended, in the order added; the moves due; the
    Results writer may give; and the index of the Start whose Marks hold writer's Mark, None where
    none does."""

    ended: tuple[bool, ...]
    due: tuple[Move, ...]
    gives: tuple[str, ...]
    marked: int | None = None


def stands(lines: tuple[Line, ...]) -> Stands:
    """Where writer's Start stands after the lines."""
    conversation = stand(d.SESSION, lines, ROUTES)
    (run,) = conversation.runs
    marked = [i for i, s in enumerate(run.starts) if s.reports]
    return Stands(
        tuple(s.ended for s in run.starts),
        run.due,
        may_give(conversation, "writer", ROUTES),
        marked[0] if marked else None,
    )


@pytest.mark.supports("test_a_start_whose_subagent_starts_after_its_post_tool_use_is_held")
@pytest.mark.parametrize(
    ("event", "then"),
    [
        pytest.param(TIE, Stands((False,), START_WRITER, WRITTEN), id="tie"),
        pytest.param(MARK, Stands((False,), START_WRITER, WRITTEN), id="mark"),
        pytest.param(END_OF_ANOTHER, Stands((False,), START_WRITER, WRITTEN), id="end-of-another"),
    ],
)
def test_an_untied_start(event: tuple[Line, ...], then: Stands) -> None:
    """Given: writer's Start, added at its Agent call's PreToolUse and not yet tied.
    When: its tie, a Mark of its subagent's agent_id, or another subagent's end comes.
    Then: the tie leaves it running; a Mark of an agent_id that no Start ties lies on no Start, as
    the event lies outside the Run; another subagent's end leaves it running."""
    assert stands((*UNTIED, *event)) == then


@pytest.mark.supports(
    "test_a_step_marked_in_its_turn_is_added_for_the_subagents_start",
    "test_the_walkthroughs_run_moves_in_the_order_the_user_set",
    "test_a_subagent_stopped_by_task_stop_is_due_again",
    "test_a_resume_where_the_routes_open_none_moves_no_run",
)
@pytest.mark.parametrize(
    ("event", "then"),
    [
        pytest.param(MARK, Stands((False,), START_WRITER, WRITTEN, 0), id="mark"),
        pytest.param(GIVE, Stands((False,), START_REVIEWER, WRITTEN), id="give"),
        pytest.param(END_OF_FIRST, Stands((True,), START_WRITER, ()), id="end-of-its-call"),
        pytest.param(END_NAMING_NONE, Stands((True,), START_WRITER, ()), id="end-naming-none"),
        pytest.param(END_KILLED, Stands((True,), START_WRITER, ()), id="end-killed"),
        pytest.param(
            END_OF_RESUME, Stands((True,), START_WRITER, ()), id="end-naming-a-call-it-didnt-make"
        ),
        pytest.param(END_OF_ANOTHER, Stands((False,), START_WRITER, WRITTEN), id="end-of-another"),
        pytest.param(RESUME_AGAIN, Stands((False, False), START_WRITER, WRITTEN), id="resume"),
    ],
)
def test_a_running_start_with_no_result(event: tuple[Line, ...], then: Stands) -> None:
    """Given: writer's Start, tied to a01, with no Result.
    When: each line that can reach it comes.
    Then: a Mark lies on it; its Result makes reviewer's start due; any end of a01 ends it with its
    start due again, as it gave no Result; another subagent's end leaves it; a resume to it while
    it runs adds a Start beside it, with writer's start still due."""
    assert stands((*RUNNING, *event)) == then


@pytest.mark.supports(
    "test_a_result_is_added_for_the_subagents_start",
    "test_the_walkthroughs_run_moves_in_the_order_the_user_set",
    "test_a_resume_where_the_routes_open_none_moves_no_run",
)
@pytest.mark.parametrize(
    ("event", "then"),
    [
        pytest.param(MARK, Stands((False,), START_REVIEWER, WRITTEN, 0), id="mark"),
        pytest.param(GIVE, Stands((False,), START_REVIEWER, WRITTEN), id="give-again"),
        pytest.param(END_OF_FIRST, Stands((True,), START_REVIEWER, ()), id="end-of-its-call"),
        pytest.param(END_NAMING_NONE, Stands((True,), START_REVIEWER, ()), id="end-naming-none"),
        pytest.param(END_KILLED, Stands((True,), START_REVIEWER, ()), id="end-killed"),
        pytest.param(
            END_OF_ANOTHER, Stands((False,), START_REVIEWER, WRITTEN), id="end-of-another"
        ),
        pytest.param(RESUME_AGAIN, Stands((False, False), START_REVIEWER, WRITTEN), id="resume"),
    ],
)
def test_a_running_start_that_gave_its_result(event: tuple[Line, ...], then: Stands) -> None:
    """Given: writer's Start, tied to a01, that gave `written`, so reviewer's start is due.
    When: each line that can reach it comes.
    Then: a Mark lies on it; its Result given again leaves reviewer's start due; any end of a01
    ends it with no start due again, as it gave its Result; a resume adds a Start beside it."""
    assert stands((*GAVE_RUNNING, *event)) == then


@pytest.mark.supports(
    "test_a_subagent_stopped_by_task_stop_is_due_again",
    "test_a_resume_where_the_routes_open_none_moves_no_run",
)
@pytest.mark.parametrize(
    ("state", "event", "then"),
    [
        pytest.param(
            ENDED_BARE,
            END_OF_ANOTHER,
            Stands((True,), START_WRITER, ()),
            id="ended-bare-end-of-another",
        ),
        pytest.param(
            ENDED_BARE,
            RESUME_AGAIN,
            Stands((True, False), START_WRITER, WRITTEN),
            id="ended-bare-resume",
        ),
        pytest.param(
            ENDED_GAVE,
            END_OF_ANOTHER,
            Stands((True,), START_REVIEWER, ()),
            id="ended-gave-end-of-another",
        ),
        pytest.param(
            ENDED_GAVE,
            RESUME_AGAIN,
            Stands((True, False), START_REVIEWER, WRITTEN),
            id="ended-gave-resume",
        ),
    ],
)
def test_an_ended_start(state: tuple[Line, ...], event: tuple[Line, ...], then: Stands) -> None:
    """Given: writer's Start ended, with no Result or with `written`.
    When: another subagent's end, or a resume to its subagent that no Route opens, comes.
    Then: another's end leaves it as it stands; the resume adds a running Start of writer, which
    may give its Results, and leaves the moves due as they stand."""
    assert stands((*state, *event)) == then


@pytest.mark.supports(
    "test_an_end_that_reaches_after_a_resume_ends_only_the_pass_it_names",
    "test_a_resume_where_the_routes_open_none_moves_no_run",
)
@pytest.mark.parametrize(
    ("event", "then"),
    [
        pytest.param(MARK, Stands((False, False), START_REVIEWER, WRITTEN, 1), id="mark"),
        pytest.param(GIVE, Stands((False, False), START_REVIEWER, WRITTEN), id="give"),
        pytest.param(
            END_OF_FIRST, Stands((True, False), START_REVIEWER, WRITTEN), id="end-of-the-first-call"
        ),
        pytest.param(
            END_OF_RESUME, Stands((True, True), START_REVIEWER, ()), id="end-of-the-resume"
        ),
        pytest.param(
            END_NAMING_NONE, Stands((True, True), START_REVIEWER, ()), id="end-naming-none"
        ),
        pytest.param(END_KILLED, Stands((True, True), START_REVIEWER, ()), id="end-killed"),
        pytest.param(
            END_OF_ANOTHER, Stands((False, False), START_REVIEWER, WRITTEN), id="end-of-another"
        ),
        pytest.param(
            RESUME_AGAIN,
            Stands((False, False, False), START_REVIEWER, WRITTEN),
            id="resume-again",
        ),
    ],
)
def test_a_start_resumed_before_its_end(event: tuple[Line, ...], then: Stands) -> None:
    """Given: writer's Start that gave `written`, and a resume of a01 that no Route opens, before
    the end of the first call reaches the main conversation.
    When: each line that can reach them comes.
    Then: a Mark lies on the resume; the end of the first call ends only the first Start; the end
    of the resume, or one naming no call, ends both; another's end leaves both running."""
    assert stands((*RESUMED_BEFORE_END, *event)) == then


@pytest.mark.supports(
    "test_a_resume_where_the_routes_open_none_moves_no_run",
    "test_a_subagent_stopped_by_task_stop_is_due_again",
)
@pytest.mark.parametrize(
    ("event", "then"),
    [
        pytest.param(MARK, Stands((True, False), START_REVIEWER, WRITTEN, 1), id="mark"),
        pytest.param(
            END_OF_RESUME, Stands((True, True), START_REVIEWER, ()), id="end-of-the-resume"
        ),
        pytest.param(
            END_NAMING_NONE, Stands((True, True), START_REVIEWER, ()), id="end-naming-none"
        ),
        pytest.param(END_KILLED, Stands((True, True), START_REVIEWER, ()), id="end-killed"),
        pytest.param(
            END_OF_ANOTHER, Stands((True, False), START_REVIEWER, WRITTEN), id="end-of-another"
        ),
    ],
)
def test_a_start_resumed_after_its_end(event: tuple[Line, ...], then: Stands) -> None:
    """Given: writer's Start that gave `written` and ended, and a resume of a01 that no Route opens.
    When: each line that can reach the resume comes.
    Then: a Mark lies on the resume; any end of a01 ends it, with no start due again, as no Route
    made the resume due; another's end leaves it running."""
    assert stands((*RESUMED_AFTER_END, *event)) == then


@pytest.mark.supports(
    "test_a_resume_a_route_makes_due_adds_a_start_and_moves_the_run",
    "test_a_subagent_stopped_by_task_stop_is_due_again",
)
@pytest.mark.parametrize(
    ("event", "then"),
    [
        pytest.param(MARK, Stands((True, True, False), (), WRITTEN, 2), id="mark"),
        pytest.param(GIVE, Stands((True, True, False), START_REVIEWER, WRITTEN), id="give"),
        pytest.param(
            END_OF_RESUME, Stands((True, True, True), START_WRITER, ()), id="end-of-the-resume"
        ),
        pytest.param(END_KILLED, Stands((True, True, True), START_WRITER, ()), id="end-killed"),
    ],
)
def test_a_resume_a_route_opened(event: tuple[Line, ...], then: Stands) -> None:
    """Given: writer's first pass ended with `written`, reviewer's `more`, and the resume of a01
    that `more` opens, which takes the resume due.
    When: each line that can reach the resume comes.
    Then: a Mark lies on the resume; its Result makes reviewer's start due; its end with no Result
    makes writer's start due again, as a Route made it due."""
    assert stands((*RESUMED_OPENED, *event)) == then


class RunStands(NamedTuple):
    """What a Run's state leaves: the moves due, whether it awaits the adapter, has ended, and is
    closing."""

    due: tuple[Move, ...]
    awaiting: bool
    ended: bool
    closing: bool


def run_stands(lines: tuple[Line, ...]) -> RunStands:
    """Where the Run stands after the lines."""
    (run,) = stand(d.SESSION, lines, ROUTES, "changelog").runs
    return RunStands(run.due, run.awaiting, run.ended, run.closing)


AWAITING = (CALLED, TextFailed("r1"))
CLOSING = (
    CALLED,
    Started("r1", "reviewer", "Carry out your steps", {}, "toolu_r", False),
    Tied("r1", "toolu_r", "a02"),
    Gave("r1", "reviewer", "good", "a02"),
    Gave("r1", "write", "good", None),
)
CLOSED = (*CLOSING, Prompted("r1", "thanks"))
REPLY = (Prompted("r1", "yes"),)
PAUSE = (Prompted("r1", "/changelog:pause"),)
PAUSED = (Move("no_more", result="paused"),)


@pytest.mark.supports(
    "test_a_command_a_route_goes_after_takes_the_place_of_the_moves_due",
    "test_a_start_whose_adapter_failed_at_the_call_is_given_once_it_gives_its_text",
    "test_the_skills_end_held_to_its_command_goes_once_it_gives_0",
    "test_a_move_that_waits_for_the_person_lets_the_turn_end",
)
@pytest.mark.parametrize(
    ("state", "event", "then"),
    [
        pytest.param(
            (CALLED,), REPLY, RunStands(START_WRITER, False, False, False), id="going-reply"
        ),
        pytest.param((CALLED,), PAUSE, RunStands(PAUSED, False, False, False), id="going-command"),
        pytest.param(
            (CALLED,),
            (TextGiven("r1"),),
            RunStands(START_WRITER, False, False, False),
            id="going-text-given-unawaited",
        ),
        pytest.param(
            AWAITING, REPLY, RunStands(START_WRITER, True, False, False), id="awaiting-reply"
        ),
        pytest.param(AWAITING, PAUSE, RunStands(PAUSED, True, False, False), id="awaiting-command"),
        pytest.param(
            AWAITING,
            (TextFailed("r1"),),
            RunStands(START_WRITER, True, False, False),
            id="awaiting-text-failed-again",
        ),
        pytest.param(
            AWAITING,
            (TextGiven("r1"),),
            RunStands(START_WRITER, False, False, False),
            id="awaiting-text-given",
        ),
        pytest.param(CLOSING, REPLY, RunStands((), False, True, False), id="closing-reply"),
        pytest.param(CLOSING, PAUSE, RunStands(PAUSED, False, True, False), id="closing-command"),
        pytest.param(CLOSED, REPLY, RunStands((), False, True, False), id="closed-reply"),
    ],
)
def test_a_runs_state(state: tuple[Line, ...], event: tuple[Line, ...], then: RunStands) -> None:
    """Given: a Run going, awaiting the adapter of a start's text, closing after its skill's
    Result, or closed by a prompt after it.
    When: a reply, a command a Route goes after, or the adapter's failure or answer comes.
    Then: a reply leaves the moves due; the command takes their place; the adapter's answer ends
    the awaiting, and a failure keeps it; a Run that ended stays ended, and a prompt ends its
    closing."""
    assert run_stands((*state, *event)) == then
