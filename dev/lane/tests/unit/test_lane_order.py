"""The unit cases of hooks/lane/order.py's order_run: one for each kind of entry of the run record,
given to the order as a move or left out, with the transitions of a start that Lane's list of Claude
Code's states brings about: made, tied, dropped as its Agent call failed, stopped with no result,
resumed, and ended with its result."""

from __future__ import annotations

import lane_entries
import pytest
from order import OrderMove, order_run
from record import Entry, Run

pytestmark = pytest.mark.xfail(strict=True, reason="Lane's parts have no bodies yet")

COMMAND: OrderMove = {"kind": "command", "command": "log:up"}
START: Entry = lane_entries.start("u1", prompt="Write the entry.")
TIE: Entry = lane_entries.tie("u1", "a1")
STARTED: OrderMove = {"kind": "start", "role": "log:writer", "prompt": "Write the entry."}


def run(*entries: Entry) -> Run:
    """The run r1 of log:up for 1.2.0, with its folder and the entries after."""
    head: list[Entry] = [
        {"kind": "run", "run": "r1", "skill": "log:up", "words": "1.2.0"},
        {"kind": "folder", "run": "r1", "plugin_root": "/plugins/log"},
    ]
    return Run("r1", "session-1", "log:up", "1.2.0", "/plugins/log", [*head, *entries])


@pytest.mark.supports("test_the_turns_end_while_the_commands_start_is_due_is_stopped_with_it")
def test_a_run_with_no_move_after_its_call_gives_its_skill_words_and_command():
    """Given a run of log:up for 1.2.0 with nothing after its folder
    When Lane gives the run as the order sees it
    Then it holds the skill, the words, and the command that called it"""
    assert order_run(run()) == {"skill": "log:up", "words": "1.2.0", "moves": [COMMAND]}


@pytest.mark.supports("test_the_order_tells_the_starts_of_one_role_apart_by_their_prompts")
@pytest.mark.parametrize("tied", [False, True])
def test_a_start_is_given_with_its_role_and_prompt(tied: bool):
    """Given the writer's start with its prompt, untied or tied to a1
    When Lane gives the run as the order sees it
    Then it holds the start with its role and prompt, and nothing of the tie"""
    entries = (START, TIE) if tied else (START,)
    assert order_run(run(*entries))["moves"] == [COMMAND, STARTED]


@pytest.mark.supports("test_a_result_reaching_the_main_conversation_gives_the_starts_due_after_it")
def test_a_result_is_given_with_its_role():
    """Given the writer's start, tied to a1, and a1's result `written`
    When Lane gives the run as the order sees it
    Then it holds the start, and then the result with its role"""
    gave: Entry = lane_entries.result("a1", "written")
    result: OrderMove = {"kind": "result", "role": "log:writer", "result": "written"}
    assert order_run(run(START, TIE, gave))["moves"] == [COMMAND, STARTED, result]


@pytest.mark.supports("test_a_typed_command_that_a_route_goes_after_puts_its_starts_in_place")
def test_a_typed_command_is_given_by_its_skills_name():
    """Given the person's /log:retry typed in the run
    When Lane gives the run as the order sees it
    Then it holds log:retry as a command after the one that called the run"""
    typed: Entry = {"kind": "typed", "run": "r1", "command": "log:retry"}
    retry: OrderMove = {"kind": "command", "command": "log:retry"}
    assert order_run(run(typed))["moves"] == [COMMAND, retry]


@pytest.mark.supports("test_an_agent_call_that_fails_after_its_pre_tool_use_leaves_its_start_due")
def test_a_start_dropped_as_its_agent_call_failed_is_left_out():
    """Given the writer's start, dropped as its Agent call failed
    When Lane gives the run as the order sees it
    Then it holds no start, so that the order gives the writer due again"""
    dropped: Entry = {"kind": "drop", "run": "r1", "tool_use_id": "u1"}
    assert order_run(run(START, dropped))["moves"] == [COMMAND]


@pytest.mark.supports("test_a_subagent_stopped_by_task_stop_is_due_again")
def test_a_start_stopped_with_no_result_is_left_out():
    """Given the writer's start, tied to a1, which TaskStop stopped with no result
    When Lane gives the run as the order sees it
    Then it holds no start, so that the order gives the writer due again"""
    stopped: Entry = {"kind": "stopped", "run": "r1", "agent_id": "a1"}
    assert order_run(run(START, TIE, stopped))["moves"] == [COMMAND]


@pytest.mark.supports("test_a_resume_that_the_order_makes_due_goes_through_as_its_start")
def test_a_resume_is_given_as_a_start_with_the_prompt_of_the_start_it_resumes():
    """Given the writer's start tied to a1, and a resume of a1 by SendMessage, tied to it
    When Lane gives the run as the order sees it
    Then it holds two starts of the writer, each with the first start's prompt"""
    resume: Entry = {**START, "tool_use_id": "u2"}
    tied: Entry = lane_entries.tie("u2", "a1")
    assert order_run(run(START, TIE, resume, tied))["moves"] == [COMMAND, STARTED, STARTED]


@pytest.mark.supports("test_a_read_whole_holds_the_mark")
def test_reads_and_marks_are_left_out():
    """Given the writer's read and its mark of a step
    When Lane gives the run as the order sees it
    Then it holds none of them, as the order is given commands, starts, and results alone"""
    read: Entry = {
        "kind": "read",
        "run": "r1",
        "agent_id": "a1",
        "path": "NOTES.md",
        "first_line": 1,
        "last_line": 6,
    }
    mark: Entry = {"kind": "mark", "run": "r1", "agent_id": "a1", "step": "write"}
    assert order_run(run(START, TIE, read, mark))["moves"] == [COMMAND, STARTED]
