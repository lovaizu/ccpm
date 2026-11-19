"""The unit cases of Lane's route adapter, adapters/routes.py: one for each transition of a run's
starts due that Lane's list of Claude Code's states brings about, from the run that the order is
given: the command's route, a start made, dropped, tied, or stopped with no result, each result and
its route, a typed command in place of what was due, the command that called the run typed again,
two starts of one role, a result that no route goes after, and the end of the routes."""

from __future__ import annotations

from typing import Any

import lane_bench
import pytest
from adapters import OrderMove, OrderRun, StartDue
from routes import starts_due

pytestmark = pytest.mark.xfail(strict=True, reason="Lane's parts have no bodies yet")

ROUTES: Any = lane_bench.RULES["routes"]


def run(*moves: OrderMove | None) -> OrderRun:
    """The run of log:up for 1.2.0 as its order sees it: its command, and the moves after it, a
    move that the order isn't given left out."""
    head: list[OrderMove] = [{"kind": "command", "command": "log:up"}]
    return {"skill": "log:up", "words": "1.2.0", "moves": [*head, *(m for m in moves if m)]}


def start(role: str, use: str) -> OrderMove:
    return {"kind": "start", "role": role}


def tie(use: str, agent_id: str) -> None:
    """A start tied to its subagent, which the order isn't given."""


def result(role: str, agent_id: str, value: str) -> OrderMove:
    return {"kind": "result", "role": role, "result": value}


def roles(starts: list[StartDue]) -> list[str]:
    return [each["role"] for each in starts for _ in range(each["count"])]


WRITER_DONE = (start("log:writer", "u1"), tie("u1", "a1"), result("log:writer", "a1", "written"))


@pytest.mark.supports("test_the_turns_end_while_the_commands_start_is_due_is_stopped_with_it")
def test_a_run_with_only_its_command_has_the_commands_starts_due():
    """Given a run of log:up with no move after its folder
    When Lane gives the starts due
    Then the writer is due, with no text yet"""
    assert starts_due(ROUTES, run()) == [{"role": "log:writer", "count": 1}]


@pytest.mark.supports("test_the_start_due_goes_through_and_leaves_none_due")
def test_a_start_made_of_the_role_due_leaves_none_due():
    """Given the writer due, and a start of the writer, not yet tied
    When Lane gives the starts due
    Then none is due"""
    assert starts_due(ROUTES, run(start("log:writer", "u1"))) == []


@pytest.mark.supports("test_the_start_due_goes_through_and_leaves_none_due")
def test_a_start_tied_to_its_subagent_leaves_none_due():
    """Given the writer's start, tied to its subagent
    When Lane gives the starts due
    Then none is due"""
    assert starts_due(ROUTES, run(start("log:writer", "u1"), tie("u1", "a1"))) == []


@pytest.mark.supports("test_an_agent_call_that_fails_after_its_pre_tool_use_leaves_its_start_due")
def test_a_start_dropped_is_due_again():
    """Given the writer's start, dropped as its Agent call failed
    When Lane gives the starts due
    Then the writer is due again"""
    dropped = None  # A start dropped is left out of the run that the order is given.
    assert roles(starts_due(ROUTES, run(start("log:writer", "u1"), dropped))) == ["log:writer"]


@pytest.mark.supports("test_a_subagent_stopped_by_task_stop_is_due_again")
def test_a_start_stopped_with_no_result_is_due_again():
    """Given the writer's start, tied to a1, which TaskStop stopped with no result
    When Lane gives the starts due
    Then the writer is due again"""
    stopped = None  # A start stopped with no result is left out of the run that the order is given.
    assert roles(starts_due(ROUTES, run(start("log:writer", "u1"), tie("u1", "a1"), stopped))) == [
        "log:writer"
    ]


@pytest.mark.supports(
    "test_a_result_reaching_the_main_conversation_gives_the_starts_its_route_makes_due"
)
def test_a_result_makes_the_starts_of_its_route_due():
    """Given the writer's result `written`
    When Lane gives the starts due
    Then the reviewer is due"""
    assert roles(starts_due(ROUTES, run(*WRITER_DONE))) == ["log:reviewer"]


@pytest.mark.supports("test_a_typed_command_that_a_route_waits_for_puts_its_starts_in_place")
def test_a_typed_command_puts_its_routes_starts_in_place_of_those_before():
    """Given the reviewer due after the writer's `written`
    When the person's /log:retry is added, and Lane gives the starts due
    Then the writer is due, and not the reviewer"""
    typed: OrderMove = {"kind": "command", "command": "log:retry"}
    assert roles(starts_due(ROUTES, run(*WRITER_DONE, typed))) == ["log:writer"]


@pytest.mark.supports("test_the_command_typed_after_compact_gives_where_the_run_picks_up")
def test_the_command_that_called_the_run_given_again_leaves_the_starts_as_they_stand():
    """Given the reviewer due after the writer's `written`
    When the person's /log:up is added again, and Lane gives the starts due
    Then the reviewer is due, and not the writer that the route after /log:up starts"""
    typed: OrderMove = {"kind": "command", "command": "log:up"}
    assert roles(starts_due(ROUTES, run(*WRITER_DONE, typed))) == ["log:reviewer"]


@pytest.mark.supports("test_two_starts_of_one_role_are_each_held_to_their_own_start")
def test_two_starts_of_one_role_are_due_until_each_is_made():
    """Given the reviewer's `split`, which makes two writers due, and one writer's start
    When Lane gives the starts due before and after that start
    Then two writers are due before it, and one after"""
    split = (
        *WRITER_DONE,
        start("log:reviewer", "u2"),
        tie("u2", "a2"),
        result("log:reviewer", "a2", "split"),
    )
    assert roles(starts_due(ROUTES, run(*split))) == ["log:writer", "log:writer"]
    after = run(*split, start("log:writer", "u3"))
    assert roles(starts_due(ROUTES, after)) == ["log:writer"]


@pytest.mark.supports("test_a_run_whose_routes_start_no_more_ends_and_holds_no_move_after")
def test_a_result_whose_route_starts_none_leaves_none_due():
    """Given the reviewer's `good`, whose route starts no role
    When Lane gives the starts due
    Then none is due, which ends the run"""
    good = (*WRITER_DONE, start("log:reviewer", "u2"), result("log:reviewer", "a2", "good"))
    assert starts_due(ROUTES, run(*good)) == []


@pytest.mark.supports("test_the_reviewers_more_makes_the_writer_due_again")
def test_the_latest_result_decides_the_starts_due():
    """Given the writer's `written`, then the reviewer's `more`
    When Lane gives the starts due
    Then the writer is due, by the route of the latest result"""
    more = (*WRITER_DONE, start("log:reviewer", "u2"), result("log:reviewer", "a2", "more"))
    assert roles(starts_due(ROUTES, run(*more))) == ["log:writer"]


@pytest.mark.supports("test_a_new_conversation_picks_the_run_up_from_the_kept_results")
def test_kept_results_with_no_start_make_the_starts_of_the_latest_due():
    """Given a run picked up with the writer's kept `written`, which no start of the run gave
    When Lane gives the starts due
    Then the reviewer is due"""
    kept = result("log:writer", "", "written")
    assert roles(starts_due(ROUTES, run(kept))) == ["log:reviewer"]
