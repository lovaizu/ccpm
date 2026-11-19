"""The unit cases of Lane's route adapter, hooks/lane/routes.py: one for each transition of a run's
starts due that Lane's list of Claude Code's states brings about, from the run that the order is
given: the command's route, a start made, each result and its route, a typed command in place of
what was due, the command that called the run given again, a role named twice in a route, a route
that starts none, a result or a command that no route goes after, and a start that still runs."""

from __future__ import annotations

from typing import Any

import lane_bench
import pytest
from order import OrderMove, OrderRun
from routes import starts_due

ROUTES: Any = lane_bench.RULES["routes"]


def run(*moves: OrderMove) -> OrderRun:
    """The run of log:up for 1.2.0 as its order sees it: its command, and the moves after it."""
    head: list[OrderMove] = [{"kind": "command", "command": "log:up"}]
    return {"skill": "log:up", "words": "1.2.0", "moves": [*head, *moves]}


def start(role: str) -> OrderMove:
    return {"kind": "start", "role": role, "prompt": f"You are {role}."}


def result(role: str, value: str) -> OrderMove:
    return {"kind": "result", "role": role, "result": value}


def command(skill: str) -> OrderMove:
    return {"kind": "command", "command": skill}


def due(role: str, count: int = 1) -> Any:
    return {"starts": [{"role": role, "count": count}]}


WAITS = {"starts": []}
ENDS = {"ends": True}
WRITTEN = (start("log:writer"), result("log:writer", "written"))


def reviewed(value: str) -> tuple[OrderMove, ...]:
    """The writer's `written`, and then the reviewer's result."""
    return (*WRITTEN, start("log:reviewer"), result("log:reviewer", value))


@pytest.mark.supports("test_the_turns_end_while_the_commands_start_is_due_is_stopped_with_it")
def test_a_run_with_only_its_command_has_the_commands_starts_due():
    """Given a run of log:up with no move after its command
    When Lane gives the starts due
    Then the writer is due"""
    assert starts_due(ROUTES, run()) == due("log:writer")


@pytest.mark.supports("test_the_run_waits_while_the_start_its_route_made_due_runs")
def test_a_start_made_of_the_role_due_that_still_runs_leaves_the_run_waiting():
    """Given the writer due, and a start of it with no result yet
    When Lane gives the starts due
    Then none is due, and the run doesn't end"""
    assert starts_due(ROUTES, run(start("log:writer"))) == WAITS


@pytest.mark.supports("test_a_result_reaching_the_main_conversation_gives_the_starts_due_after_it")
def test_a_result_makes_the_starts_of_its_route_due():
    """Given the writer's result `written`
    When Lane gives the starts due
    Then the reviewer is due"""
    assert starts_due(ROUTES, run(*WRITTEN)) == due("log:reviewer")


@pytest.mark.supports("test_the_reviewers_more_makes_the_writer_due_again")
def test_the_latest_result_decides_the_starts_due():
    """Given the writer's `written`, then the reviewer's `more`
    When Lane gives the starts due
    Then the writer is due, by the route of the latest result"""
    assert starts_due(ROUTES, run(*reviewed("more"))) == due("log:writer")


@pytest.mark.supports("test_a_typed_command_that_a_route_goes_after_puts_its_starts_in_place")
def test_a_typed_command_puts_its_routes_starts_in_place_of_those_before():
    """Given the reviewer due after the writer's `written`
    When the person's /log:retry is added, and Lane gives the starts due
    Then the writer is due, and not the reviewer"""
    assert starts_due(ROUTES, run(*WRITTEN, command("log:retry"))) == due("log:writer")


@pytest.mark.supports("test_the_command_typed_after_compact_gives_where_the_run_stands")
def test_the_command_that_called_the_run_given_again_leaves_the_starts_as_they_stand():
    """Given the reviewer due after the writer's `written`
    When the person's /log:up is added again, and Lane gives the starts due
    Then the reviewer is due, and not the writer that the route after /log:up starts"""
    assert starts_due(ROUTES, run(*WRITTEN, command("log:up"))) == due("log:reviewer")


@pytest.mark.supports("test_a_role_named_twice_in_a_route_is_due_twice_at_once")
@pytest.mark.parametrize("made, count", [(0, 2), (1, 1)])
def test_a_role_named_twice_in_a_route_is_due_as_many_times_less_each_start_made(
    made: int, count: int
):
    """Given the reviewer's `split`, whose route names the writer twice, and no start of the writer
    after it, or one
    When Lane gives the starts due
    Then the writer is due twice at once, or once"""
    moves = (*reviewed("split"), *[start("log:writer")] * made)
    assert starts_due(ROUTES, run(*moves)) == due("log:writer", count)


@pytest.mark.supports("test_a_role_named_twice_in_a_route_is_due_twice_at_once")
def test_each_start_of_a_role_named_twice_made_and_running_leaves_the_run_waiting():
    """Given the reviewer's `split`, and both writers' starts with no result yet
    When Lane gives the starts due
    Then none is due, and the run doesn't end"""
    moves = (*reviewed("split"), start("log:writer"), start("log:writer"))
    assert starts_due(ROUTES, run(*moves)) == WAITS


@pytest.mark.supports("test_a_run_whose_order_says_it_ends_holds_no_move_after")
def test_a_result_whose_route_starts_none_ends_the_run():
    """Given the reviewer's `good`, whose route starts no role, and no start running
    When Lane gives the starts due
    Then the run ends"""
    assert starts_due(ROUTES, run(*reviewed("good"))) == ENDS


@pytest.mark.supports("test_a_result_that_no_route_goes_after_ends_the_run_once_no_start_runs")
def test_a_result_that_no_route_goes_after_ends_the_run():
    """Given the writer's `unclear`, which no route goes after, and no start running
    When Lane gives the starts due
    Then the run ends"""
    assert starts_due(ROUTES, run(start("log:writer"), result("log:writer", "unclear"))) == ENDS


@pytest.mark.supports("test_a_result_that_no_route_goes_after_ends_the_run_once_no_start_runs")
def test_a_result_that_no_route_goes_after_leaves_the_run_waiting_while_a_start_runs():
    """Given the reviewer's `split`, two writers' starts, and the first's `unclear`, which no route
    goes after, while the second runs
    When Lane gives the starts due
    Then none is due, and the run doesn't end"""
    moves = (
        *reviewed("split"),
        start("log:writer"),
        start("log:writer"),
        result("log:writer", "unclear"),
    )
    assert starts_due(ROUTES, run(*moves)) == WAITS


@pytest.mark.supports("test_a_result_that_no_route_goes_after_ends_the_run_once_no_start_runs")
def test_a_command_that_no_route_goes_after_ends_the_run():
    """Given routes that go after no command, and a run with only its command
    When Lane gives the starts due
    Then the run ends"""
    after_results = [each for each in ROUTES if "command" not in each["after"]]
    assert starts_due(after_results, run()) == ENDS
