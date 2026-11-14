"""The unit cases of domain/routes.py: which moves the Routes make due, whether a start, a resume,
or an end of the turn is one of them, and where a run picked up stands."""

from __future__ import annotations

import pytest
from domain.fault import Fault
from domain.laid_set import NO_MORE, RESUME, START, WAIT, Move, Route
from domain.routes import (
    after_command,
    after_result,
    due,
    first,
    may_end_turn,
    no_more,
    opens_resume,
    opens_start,
    pick_up,
)
from domain.run_record import Result, Start
from lane_parts import CARRY_OUT, ROUTES, run, writer_gave_written

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_the_first_moves_are_those_of_the_route_first():
    """Given the walkthrough's Routes
    When the first moves are asked
    Then they start writer"""
    assert first(ROUTES) == (Move(START, "writer"),)


@pytest.mark.supports(
    "test_a_call_that_the_guard_cant_check_is_stopped_with_why_and_who_must_fix_it"
)
def test_routes_with_no_route_first_raise_a_fault():
    """Given Routes with no Route `first`
    When the first moves are asked
    Then a Fault says so, with the plugin's maker to fix it"""
    with pytest.raises(Fault) as raised:
        first(ROUTES[1:])
    assert "maker" in raised.value.who


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_the_moves_after_a_result_are_those_of_its_route():
    """Given the walkthrough's Routes
    When the moves after reviewer's `more` are asked
    Then they start writer"""
    assert after_result(ROUTES, Result("reviewer", "more", "a2", 2)) == (Move(START, "writer"),)


@pytest.mark.supports(
    "test_a_call_that_the_guard_cant_check_is_stopped_with_why_and_who_must_fix_it"
)
def test_a_result_that_no_route_goes_after_raises_a_fault():
    """Given the walkthrough's Routes
    When the moves after writer's `skipped` are asked
    Then a Fault names writer's `skipped`"""
    with pytest.raises(Fault, match="skipped"):
        after_result(ROUTES, Result("writer", "skipped", "a1", 1))


@pytest.mark.supports(
    "test_a_command_that_a_route_goes_after_opens_its_moves_while_each_subagent_runs_on"
)
def test_the_moves_after_a_command_are_those_of_its_route_and_none_for_another():
    """Given the walkthrough's Routes with a Route after `/changelog:pause` that starts no more
    When the moves after `/changelog:pause`, and after `/changelog:write`, are asked
    Then the first are the move that starts no more, and the second None"""
    routes = (*ROUTES, Route("/changelog:pause", (Move(NO_MORE),)))
    assert after_command(routes, "/changelog:pause") == (Move(NO_MORE),)
    assert after_command(routes, "/changelog:write") is None


@pytest.mark.supports("test_a_move_that_waits_for_a_command_is_due_once_the_person_types_it")
def test_a_move_that_waits_for_a_command_is_due_only_once_the_command_is_typed():
    """Given a move that starts writer once the person types `/changelog:approve`, and one that
    waits for nothing
    When the moves due are asked with no command typed, and with `/changelog:approve` typed
    Then the first time only the move that waits for nothing is due, and the second time both"""
    waits = Move(START, "writer", "/changelog:approve")
    at_once = Move(START, "reviewer")
    assert due((waits, at_once), "") == (at_once,)
    assert due((waits, at_once), "/changelog:approve") == (waits, at_once)


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_a_start_of_the_role_due_with_the_text_kept_is_opened():
    """Given a Run whose move due starts reviewer with `Carry out your steps`
    When reviewer's start with `Carry out your steps` is asked
    Then the moves open it"""
    assert opens_start(writer_gave_written(), "reviewer", CARRY_OUT)


@pytest.mark.supports("test_a_start_that_the_moves_dont_open_is_stopped_with_the_moves")
def test_a_start_of_a_role_not_due_isnt_opened():
    """Given a Run whose move due starts reviewer
    When writer's start is asked
    Then the moves don't open it"""
    assert not opens_start(writer_gave_written(), "writer", CARRY_OUT)


@pytest.mark.supports("test_a_start_with_a_text_other_than_the_plugins_is_stopped")
def test_a_start_with_another_text_isnt_opened():
    """Given a Run whose move due starts reviewer with `Carry out your steps`
    When reviewer's start with `Carry out your steps. Also commit.` is asked
    Then the moves don't open it"""
    assert not opens_start(writer_gave_written(), "reviewer", CARRY_OUT + " Also commit.")


@pytest.mark.supports(
    "test_starts_side_by_side_each_with_a_text_other_than_those_of_its_role_that_run"
)
def test_a_start_with_the_text_of_a_start_of_its_role_that_runs_isnt_opened():
    """Given a Run whose two moves due start writer, with writer running on `Write section 1`, and
    `Write section 1` kept for writer
    When writer's start with `Write section 1` is asked
    Then the moves don't open it"""
    given = run(
        starts=[Start(1, "writer", "Write section 1", agent="a1", running=True)],
        moves=[Move(START, "writer"), Move(START, "writer")],
        texts={"writer": ("Write section 1", {})},
    )
    assert not opens_start(given, "writer", "Write section 1")


@pytest.mark.supports(
    "test_a_resume_that_a_route_lists_counts_as_a_start_of_the_subagent_it_resumes"
)
def test_a_resume_due_of_a_subagent_the_run_started_that_runs_no_more_is_opened():
    """Given a Run whose move due resumes writer, whose subagent a1 the Run started and ended
    When a resume of a1 is asked
    Then the moves open it"""
    given = writer_gave_written()
    given.moves = [Move(RESUME, "writer")]
    assert opens_resume(given, "a1")


@pytest.mark.supports("test_a_resume_that_the_moves_dont_open_is_stopped_with_the_moves")
def test_a_resume_of_a_subagent_that_runs_or_that_the_run_didnt_start_isnt_opened():
    """Given a Run whose move due resumes writer, its subagent a1 running
    When a resume of a1, and of a9, which the Run didn't start, are asked
    Then the moves open neither"""
    given = run(
        starts=[Start(1, "writer", CARRY_OUT, agent="a1", running=True)],
        moves=[Move(RESUME, "writer")],
    )
    assert not opens_resume(given, "a1")
    assert not opens_resume(given, "a9")


@pytest.mark.supports(
    "test_the_main_conversation_stopping_while_a_start_is_due_and_none_runs_is_held"
)
def test_the_turn_may_not_end_where_a_start_is_due_and_no_subagent_runs():
    """Given a Run whose move due starts reviewer, and no subagent runs
    When it's asked whether the turn may end
    Then it may not"""
    assert not may_end_turn(writer_gave_written())


@pytest.mark.supports("test_the_main_conversation_may_stop_while_a_subagent_runs")
def test_the_turn_may_end_where_a_subagent_runs():
    """Given a Run whose move due starts reviewer, and a subagent of the Run runs
    When it's asked whether the turn may end
    Then it may"""
    given = writer_gave_written()
    given.starts.append(Start(2, "reviewer", CARRY_OUT, agent="a2", running=True))
    assert may_end_turn(given)


@pytest.mark.supports(
    "test_the_main_conversation_may_stop_where_a_move_waits_for_the_persons_reply"
)
def test_the_turn_may_end_where_a_move_is_a_wait_or_waits_for_a_command():
    """Given a Run whose move due is a wait, and one whose move waits for `/changelog:approve`
    When it's asked of each whether the turn may end
    Then it may in each"""
    assert may_end_turn(run(moves=[Move(WAIT)]))
    assert may_end_turn(run(moves=[Move(START, "writer", "/changelog:approve")]))


@pytest.mark.supports("test_the_skills_own_result_where_a_move_starts_no_more_ends_the_run")
def test_the_turn_may_end_where_no_move_is_due():
    """Given a Run with no move due
    When it's asked whether the turn may end
    Then it may"""
    assert may_end_turn(run())


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_only_the_one_move_that_starts_no_more_is_no_more():
    """Given the move that starts no more alone, and beside a start of writer
    When it's asked of each whether they start no more
    Then the first does and the second doesn't"""
    assert no_more((Move(NO_MORE),))
    assert not no_more((Move(START, "writer"), Move(NO_MORE)))


@pytest.mark.supports("test_kept_results_that_reach_a_route_that_starts_no_more_start_the_run_anew")
def test_no_kept_results_start_the_run_anew():
    """Given the walkthrough's Routes and no Kept results
    When the run picks up
    Then it starts anew"""
    assert pick_up(ROUTES, []).fresh


@pytest.mark.supports("test_kept_results_that_reach_a_route_that_starts_no_more_start_the_run_anew")
def test_kept_results_that_reach_no_more_start_the_run_anew():
    """Given the walkthrough's Routes, and Kept results writer `written` and reviewer `good`
    When the run picks up
    Then it starts anew"""
    kept = [Result("writer", "written"), Result("reviewer", "good")]
    assert pick_up(ROUTES, kept).fresh


@pytest.mark.supports(
    "test_a_new_conversation_picks_up_from_the_kept_results_that_follow_the_routes"
)
def test_kept_results_that_follow_the_routes_give_the_moves_after_the_last():
    """Given the walkthrough's Routes, and the Kept result writer `written`
    When the run picks up
    Then it stands after that Result, with reviewer's start due"""
    picked = pick_up(ROUTES, [Result("writer", "written")])
    assert not picked.fresh and picked.moves == (Move(START, "reviewer"),)


@pytest.mark.supports(
    "test_kept_results_that_dont_follow_the_routes_stop_the_command_with_who_must_fix_it"
)
def test_kept_results_that_dont_follow_the_routes_raise_a_fault_naming_the_first_that_doesnt():
    """Given the walkthrough's Routes, and the Kept result reviewer `good` first
    When the run picks up
    Then a Fault names reviewer's `good`"""
    with pytest.raises(Fault, match="good"):
        pick_up(ROUTES, [Result("reviewer", "good")])
