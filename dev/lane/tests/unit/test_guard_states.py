"""The state transition cases of guard.py's `handle` on the ends of a role's Start and of the main
conversation's turn: each state of writer's Start that the run record brings about, with each end
that can reach the guard there, its subagent's end, that end as it reaches the main conversation,
the main conversation's end of its turn, and a start of writer again, and the guard's answer."""

from __future__ import annotations

import os
import tempfile
from dataclasses import replace
from typing import Any, NamedTuple

import lane_data as d
import pytest
import start_states as st
from form import write_lanes
from guard import handle
from run_record import Ended, Gave, Line, Started, Tied, add, record_path

ROUTES, TEXT = st.ROUTES, st.TEXT
UNTIED, RUNNING, GAVE_RUNNING = st.UNTIED, st.RUNNING, st.GAVE_RUNNING
ENDED_BARE, ENDED_GAVE = st.ENDED_BARE, st.ENDED_GAVE
RESUMED_BEFORE_END, RESUMED_OPENED = st.RESUMED_BEFORE_END, st.RESUMED_OPENED
RESUMED_AFTER_FIRST_END = (*RESUMED_BEFORE_END, st.END_FIRST)


def notification(called: str) -> dict[str, Any]:
    """a01's end as it reaches the main conversation, naming the call it ends."""
    prompt = (
        f"<task-notification><task-id>a01</task-id><tool-use-id>{called}</tool-use-id>"
        "<status>completed</status></task-notification>"
    )
    return {"name": "UserPromptSubmit", "prompt": prompt}


# Each end that can reach the guard, and a start of writer again, as its hook event's fields.
SUBAGENTS_END = {"name": "SubagentStop", "agent_id": "a01", "last_message": "Done."}
END_OF_FIRST = notification("toolu_w")
END_OF_RESUME = notification("toolu_w2")
TURNS_END = {"name": "Stop", "last_message": "Done."}
START_AGAIN = {
    "name": "PreToolUse",
    "tool_name": "Agent",
    "tool_use_id": "toolu_w9",
    "tool_input": {"subagent_type": "changelog:writer", "prompt": TEXT},
}


class Answered(NamedTuple):
    """The guard's answer: whether it stops, and words it holds, empty to hold none."""

    stop: bool
    says: str = ""


@pytest.fixture
def plugin(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> str:
    """changelog's folder in tally, laid with the walkthrough's Lanes and the Routes above, and the
    system's temporary folder set to the case's own."""
    monkeypatch.setenv("TMPDIR", str(tmp_path / "temp"))
    monkeypatch.setattr(tempfile, "tempdir", None)
    os.makedirs(tmp_path / "temp")
    root = tmp_path / "tally" / "changelog"
    os.makedirs(tmp_path / "tally" / ".git")
    os.makedirs(root / ".claude-plugin")
    os.makedirs(root / "hooks")
    (root / ".claude-plugin" / "plugin.json").write_text('{"name": "changelog"}')
    given = d.lanes_file()
    lanes = replace(given, proposal=replace(given.proposal, routes=ROUTES))
    write_lanes(str(root / "hooks" / "lanes.json"), lanes)
    return str(root)


def answered(plugin: str, state: tuple[Line, ...], fields: dict[str, Any]) -> tuple[bool, str]:
    """The guard's answer to the event, in the state that the lines bring about."""
    record = record_path("changelog", d.SESSION)
    for line in state:
        add(record, line)
    answer = handle(d.event(**fields), plugin)
    return answer.stop, answer.words


@pytest.mark.supports(
    "test_an_end_with_no_result_is_stopped_with_its_last_steps_sentence",
    "test_an_end_that_reaches_after_a_resume_ends_only_the_pass_it_names",
    "test_a_resume_where_the_routes_open_none_moves_no_run",
    "test_a_resume_a_route_makes_due_adds_a_start_and_moves_the_run",
)
@pytest.mark.parametrize(
    ("state", "then"),
    [
        pytest.param(RUNNING, Answered(True, "End by running"), id="running-with-no-result"),
        pytest.param(GAVE_RUNNING, Answered(False), id="running-that-gave-its-result"),
        pytest.param(RESUMED_BEFORE_END, Answered(False), id="resumed-where-no-route-opens"),
        pytest.param(
            RESUMED_OPENED, Answered(True, "End by running"), id="resumed-as-a-route-opens"
        ),
    ],
)
def test_a_subagents_end_in_each_state_of_its_start(
    plugin: str, state: tuple[Line, ...], then: Answered
) -> None:
    """Given: writer's Start running with no Result or with `written`, or resumed where no Route
    opens a resume or as reviewer's `more` opens one.
    When: a01's SubagentStop comes.
    Then: an end with no Result since a Start that a Route made due is stopped with the sentence
    of the Lane on writer's last Step; an end after its Result, or of a resume that no Route
    opened, goes."""
    stop, words = answered(plugin, state, SUBAGENTS_END)
    assert stop == then.stop and then.says in words


@pytest.mark.supports(
    "test_a_subagent_stopped_by_task_stop_is_due_again",
    "test_an_end_that_reaches_after_a_resume_ends_only_the_pass_it_names",
    "test_the_walkthroughs_run_moves_in_the_order_the_user_set",
)
@pytest.mark.parametrize(
    ("state", "fields", "then"),
    [
        pytest.param(
            RUNNING, END_OF_FIRST, Answered(False, "writer ended with no Result"), id="running-end"
        ),
        pytest.param(
            GAVE_RUNNING, END_OF_FIRST, Answered(False, "writer gave `written`"), id="gave-end"
        ),
        pytest.param(
            RESUMED_BEFORE_END,
            END_OF_FIRST,
            Answered(False, "writer gave `written`"),
            id="resumed-end-of-the-first-call",
        ),
        pytest.param(
            RESUMED_AFTER_FIRST_END,
            END_OF_RESUME,
            Answered(False, "Start `changelog:reviewer`"),
            id="resumed-end-of-the-resume-that-no-route-opened",
        ),
        pytest.param(
            RESUMED_OPENED,
            END_OF_RESUME,
            Answered(False, "writer ended with no Result"),
            id="resume-a-route-opened-ended-with-no-result",
        ),
    ],
)
def test_a_subagents_end_reaching_the_main_conversation_in_each_state(
    plugin: str, state: tuple[Line, ...], fields: dict[str, Any], then: Answered
) -> None:
    """Given: writer's Start running with no Result, with `written`, resumed before the end of its
    first call, or resumed as a Route opens it.
    When: the end of a call of a01 reaches the main conversation.
    Then: the guard says the Result of the Start that the end names with the moves of its Route,
    that it ended with no Result where a Route made it due, and only the moves due where no Route
    made the resume due."""
    stop, words = answered(plugin, state, fields)
    assert stop == then.stop and then.says in words


@pytest.mark.supports(
    "test_the_turns_end_while_a_start_is_due_is_stopped",
    "test_the_turns_end_while_the_runs_subagent_runs_goes",
    "test_an_end_that_reaches_after_a_resume_ends_only_the_pass_it_names",
)
@pytest.mark.parametrize(
    ("state", "then"),
    [
        pytest.param(RUNNING, Answered(False), id="running"),
        pytest.param(
            ENDED_BARE, Answered(True, "Start `changelog:writer`"), id="ended-with-no-result"
        ),
        pytest.param(
            ENDED_GAVE, Answered(True, "Start `changelog:reviewer`"), id="ended-with-its-result"
        ),
        pytest.param(
            RESUMED_AFTER_FIRST_END, Answered(False), id="resume-running-after-the-first-end"
        ),
        pytest.param(
            UNTIED,
            Answered(True, "Start `changelog:writer`"),
            id="untied-as-another-plugins-hook-denied-its-call",
        ),
    ],
)
def test_the_turns_end_in_each_state_of_the_start(
    plugin: str, state: tuple[Line, ...], then: Answered
) -> None:
    """Given: writer's Start running, ended with no Result or with `written`, resumed and running
    after the end of its first call, or left untied at the main conversation's end of its turn, as
    another plugin's PreToolUse hook denied its Agent call after the guard let it through.
    When: the main conversation ends its turn.
    Then: it goes while a subagent of the Run runs, and is stopped with the moves due where none
    does, as the guard drops a Start still untied at the Stop."""
    stop, words = answered(plugin, state, TURNS_END)
    assert stop == then.stop and then.says in words


@pytest.mark.supports("test_a_start_that_isnt_due_is_stopped_with_the_moves_due")
@pytest.mark.parametrize(
    ("state", "then"),
    [
        pytest.param(RUNNING, Answered(True), id="running"),
        pytest.param(ENDED_BARE, Answered(False), id="ended-with-no-result"),
        pytest.param(UNTIED, Answered(True), id="untied-before-its-calls-outcome"),
    ],
)
def test_a_start_of_writer_again_in_each_state(
    plugin: str, state: tuple[Line, ...], then: Answered
) -> None:
    """Given: writer's Start running, ended with no Result, or untied, its Agent call's PostToolUse
    or PostToolUseFailure not yet come.
    When: the main conversation starts writer again with the same text.
    Then: it's stopped while a Start of that text stands, and goes where the start is due again,
    as after an end with no Result."""
    stop, _ = answered(plugin, state, START_AGAIN)
    assert stop == then.stop


def answered_after(
    plugin: str, state: tuple[Line, ...], events: tuple[dict[str, Any], ...]
) -> tuple[bool, str]:
    """The guard's answer to the last of the events, each handled in turn, in the state that the
    lines bring about."""
    record = record_path("changelog", d.SESSION)
    for line in state:
        add(record, line)
    answer = None
    for fields in events:
        answer = handle(d.event(**fields), plugin)
    assert answer is not None
    return answer.stop, answer.words


def failure(called: str, tool: str = "Agent") -> dict[str, Any]:
    """The PostToolUseFailure of the main conversation's call, as Claude Code 2.1.327 sends it."""
    return {
        "name": "PostToolUseFailure",
        "tool_name": tool,
        "tool_use_id": called,
        "tool_input": {"subagent_type": "changelog:writer", "prompt": TEXT},
    }


@pytest.mark.supports("test_a_start_whose_agent_call_fails_is_due_again")
@pytest.mark.parametrize(
    ("events", "then"),
    [
        pytest.param(
            (failure("toolu_w"), START_AGAIN),
            Answered(False),
            id="its-calls-failure-then-a-start-again",
        ),
        pytest.param(
            (failure("toolu_w"), TURNS_END),
            Answered(True, "Start `changelog:writer`"),
            id="its-calls-failure-then-the-turns-end",
        ),
        pytest.param(
            (failure("toolu_x", "Bash"), START_AGAIN),
            Answered(True),
            id="another-calls-failure-then-a-start-again",
        ),
        pytest.param(
            (TURNS_END, START_AGAIN), Answered(False), id="the-turns-end-then-a-start-again"
        ),
    ],
)
def test_an_untied_start_with_each_event_that_ends_its_call(
    plugin: str, events: tuple[dict[str, Any], ...], then: Answered
) -> None:
    """Given: writer's Start untied, as the guard let its Agent call through.
    When: its call's PostToolUseFailure, another call's, or the main conversation's Stop comes,
    and then a start of writer again or the end of the turn.
    Then: the guard drops the Start at its own call's failure or at the Stop, so writer's start is
    due again and the turn's end is stopped with it; another call's failure leaves the Start."""
    stop, words = answered_after(plugin, UNTIED, events)
    assert stop == then.stop and then.says in words


# writer's first pass gave `written` and runs on, reviewer gave `more` and ended, so the Route
# after it makes a resume of writer due while a01 still runs.
OPENED_WHILE_RUNNING = (
    *GAVE_RUNNING,
    Started("r1", "reviewer", TEXT, {}, "toolu_r", False),
    Tied("r1", "toolu_r", "a02"),
    Gave("r1", "reviewer", "more", "a02"),
    Ended("r1", "a02", False, "toolu_r"),
)
QUEUE = {
    "name": "PreToolUse",
    "tool_name": "SendMessage",
    "tool_use_id": "toolu_w2",
    "tool_input": {"to": "a01", "summary": "More", "message": "Go on"},
}
QUEUED = {
    "name": "PostToolUse",
    "tool_name": "SendMessage",
    "tool_use_id": "toolu_w2",
    "tool_input": {"to": "a01", "summary": "More", "message": "Go on"},
    "tool_response": {
        "success": True,
        "message": "Message queued for delivery to a01 at its next tool round. If it finishes"
        " first, it is resumed with the message and its output will arrive in a later task"
        " notification.",
    },
}
RESUMED_START = {"name": "SubagentStart", "agent_id": "a01", "agent_type": "changelog:writer"}


@pytest.mark.supports("test_a_resume_queued_while_its_subagent_runs_starts_at_its_subagentstart")
@pytest.mark.parametrize(
    ("events", "then"),
    [
        pytest.param(
            (QUEUE, QUEUED, SUBAGENTS_END), Answered(False), id="queued-then-the-pass-before-ends"
        ),
        pytest.param(
            (QUEUE, QUEUED, SUBAGENTS_END, RESUMED_START, SUBAGENTS_END),
            Answered(True, "End by running"),
            id="queued-then-its-resume-ends-with-no-result",
        ),
    ],
)
def test_a_resume_queued_while_its_subagent_runs_with_each_end(
    plugin: str, events: tuple[dict[str, Any], ...], then: Answered
) -> None:
    """Given: writer's first pass gave `written` and runs, and reviewer's `more` made a resume of
    writer due.
    When: the main conversation sends a01 the resume, which Claude Code queues, and a01's pass
    ends, then a01 starts again on the message and ends.
    Then: the pass that gave `written` ends, as the resume is no Start until a01's SubagentStart,
    and the resume's end with no Result is stopped with the Lane's sentence."""
    stop, words = answered_after(plugin, OPENED_WHILE_RUNNING, events)
    assert stop == then.stop and then.says in words
