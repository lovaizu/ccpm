"""The unit cases of runs.py, how each Run stands, through `stand`, `may_give`, `pick_up`, and
`where`: the moves due after each kind of line, a Run that ends, stands aside, or outlives its
Routes; the Results a role or the skill may give; Kept results that follow the Routes, end them, or
leave them; and where a script reads it all."""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any

import lane_data as d
import pytest
from adapters import KeptResult
from form import Move, write_lanes
from run_record import (
    Called,
    Ended,
    Gave,
    Prompted,
    Started,
    SteppedAside,
    Tied,
    Unreadable,
    add,
    record_path,
)
from runs import OffRoutes, Result, may_give, pick_up, stand, where

CALLED = Called("r1", "write", "person", "")
WRITER = Started("r1", "writer", "Carry out your steps", {}, "toolu_w", False)
TIED = Tied("r1", "toolu_w", "a01")
REVIEWER = Started("r1", "reviewer", "Carry out your steps", {}, "toolu_r", False)
START_WRITER = (Move("start", role="writer"),)
START_REVIEWER = (Move("start", role="reviewer"),)


@pytest.mark.supports("test_a_new_conversation_without_an_adapter_starts_over")
def test_no_lines_hold_no_run() -> None:
    """Given: a run record with no lines.
    When: stand works out the conversation.
    Then: it holds no Run."""
    assert stand(d.SESSION, (), d.ROUTES_OF_WRITE).runs == ()


@pytest.mark.supports("test_the_walkthroughs_run_moves_in_the_order_the_user_set")
def test_a_skills_call_makes_the_first_moves_due() -> None:
    """Given: the call of write, by a person.
    When: stand works out the conversation.
    Then: write's Run, by a person, has writer's start due."""
    (run,) = stand(d.SESSION, (CALLED,), d.ROUTES_OF_WRITE).runs
    assert (run.skill, run.by, run.due, run.ended) == ("write", "person", START_WRITER, False)


@pytest.mark.supports("test_the_walkthroughs_run_moves_in_the_order_the_user_set")
def test_a_start_leaves_no_move_due_until_its_result() -> None:
    """Given: write's call, and writer's Start tied to a01.
    When: stand works out the conversation.
    Then: the Run holds writer's Start, tied, with no move due."""
    (run,) = stand(d.SESSION, (CALLED, WRITER, TIED), d.ROUTES_OF_WRITE).runs
    assert [(s.role, s.agent_id) for s in run.starts] == [("writer", "a01")]
    assert run.due == ()


@pytest.mark.supports("test_the_walkthroughs_run_moves_in_the_order_the_user_set")
def test_a_result_makes_its_routes_moves_due() -> None:
    """Given: writer's Start, and its Result `written`.
    When: stand works out the conversation.
    Then: the Run holds the Result, and reviewer's start is due."""
    given = (CALLED, WRITER, TIED, Gave("r1", "writer", "written", "a01"))
    (run,) = stand(d.SESSION, given, d.ROUTES_OF_WRITE).runs
    assert run.results == (Result("writer", "written"),)
    assert run.due == START_REVIEWER


@pytest.mark.supports("test_the_walkthroughs_run_moves_in_the_order_the_user_set")
def test_the_skills_result_after_no_more_ends_the_run() -> None:
    """Given: reviewer's `good`, whose Route starts no more, and write's own Result `good`.
    When: stand works out the conversation.
    Then: the Run has ended."""
    given = (
        CALLED,
        REVIEWER,
        Tied("r1", "toolu_r", "a02"),
        Gave("r1", "reviewer", "good", "a02"),
        Gave("r1", "write", "good", None),
    )
    (run,) = stand(d.SESSION, given, d.ROUTES_OF_WRITE).runs
    assert run.ended


@pytest.mark.supports("test_a_command_a_route_goes_after_takes_the_place_of_the_moves_due")
def test_a_command_a_route_goes_after_replaces_the_moves_due() -> None:
    """Given: writer's `written`, so reviewer's start is due, then the person's /changelog:pause,
    which a Route goes after.
    When: stand works out the conversation.
    Then: only pause's moves are due."""
    routes = (
        *d.ROUTES_OF_WRITE,
        d.route(d.After("command", command="pause"), Move("no_more", result="paused")),
    )
    given = (
        CALLED,
        WRITER,
        TIED,
        Gave("r1", "writer", "written", "a01"),
        Prompted("r1", "/changelog:pause"),
    )
    (run,) = stand(d.SESSION, given, routes, "changelog").runs
    assert run.due == (Move("no_more", result="paused"),)


@pytest.mark.supports("test_a_command_of_another_plugin_leaves_the_moves_due")
def test_a_command_of_another_plugin_leaves_the_moves_due() -> None:
    """Given: writer's `written`, so reviewer's start is due, and a Route after changelog's pause,
    then the person's /other:pause.
    When: stand works out changelog's conversation.
    Then: reviewer's start is still due."""
    routes = (
        *d.ROUTES_OF_WRITE,
        d.route(d.After("command", command="pause"), Move("no_more", result="paused")),
    )
    given = (
        CALLED,
        WRITER,
        TIED,
        Gave("r1", "writer", "written", "a01"),
        Prompted("r1", "/other:pause"),
    )
    (run,) = stand(d.SESSION, given, routes, "changelog").runs
    assert run.due == START_REVIEWER


@pytest.mark.supports("test_the_run_stands_aside_while_another_plugins_skill_runs")
def test_a_call_of_another_plugins_skill_sets_the_run_aside() -> None:
    """Given: write's call, and the main conversation's call of lint:check that a move names.
    When: stand works out the conversation.
    Then: the Run stands aside."""
    (run,) = stand(d.SESSION, (CALLED, SteppedAside("r1", "lint:check")), d.ROUTES_OF_WRITE).runs
    assert run.aside


@pytest.mark.supports("test_the_move_after_another_plugins_skill_brings_the_run_back")
def test_a_start_on_an_aside_run_ends_the_aside() -> None:
    """Given: write's call, its call of lint:check that sets it aside, and writer's Start.
    When: stand works out the conversation.
    Then: the Run no longer stands aside."""
    given = (CALLED, SteppedAside("r1", "lint:check"), WRITER)
    (run,) = stand(d.SESSION, given, d.ROUTES_OF_WRITE).runs
    assert not run.aside


@pytest.mark.supports("test_a_subagent_stopped_by_task_stop_is_due_again")
def test_a_start_ended_with_no_result_is_due_again() -> None:
    """Given: writer's Start, and its end by TaskStop with no Result.
    When: stand works out the conversation.
    Then: writer's start is due again."""
    given = (CALLED, WRITER, TIED, Ended("r1", "a01", True))
    (run,) = stand(d.SESSION, given, d.ROUTES_OF_WRITE).runs
    assert run.due == START_WRITER


@pytest.mark.supports("test_a_second_skills_run_beside_the_first_keeps_its_own_routes")
def test_two_skills_calls_make_two_runs() -> None:
    """Given: the call of write, then the call of check, each with its own Route first.
    When: stand works out the conversation.
    Then: it holds two Runs, each with its own first moves due."""
    check = d.Route("check", d.After("first"), (Move("start", role="reviewer"),))
    given = (CALLED, Called("r2", "check", "person", ""))
    runs = stand(d.SESSION, given, (*d.ROUTES_OF_WRITE, check)).runs
    assert [(r.skill, r.due) for r in runs] == [("write", START_WRITER), ("check", START_REVIEWER)]


@pytest.mark.supports("test_a_lay_after_lane_updates_lays_with_the_newest_code")
def test_a_run_whose_routes_are_gone_has_no_moves_due() -> None:
    """Given: write's call, while the Routes name no skill write.
    When: stand works out the conversation.
    Then: write's Run has no moves due."""
    (run,) = stand(d.SESSION, (CALLED,), ()).runs
    assert run.due == ()


@pytest.mark.supports("test_a_result_the_role_may_not_give_is_refused")
def test_a_running_role_may_give_the_results_its_routes_go_after() -> None:
    """Given: write's Run with writer's Start running.
    When: may_give asks what writer may give.
    Then: it gives `written`."""
    c = d.conversation(d.run(starts=(d.start("writer"),), due=()))
    assert may_give(c, "writer", d.ROUTES_OF_WRITE) == ("written",)


@pytest.mark.supports("test_a_result_the_role_may_not_give_is_refused")
def test_a_role_with_no_start_running_may_give_nothing() -> None:
    """Given: write's Run, with no Start of reviewer.
    When: may_give asks what reviewer may give.
    Then: it gives none."""
    assert may_give(d.conversation(d.run()), "reviewer", d.ROUTES_OF_WRITE) == ()


@pytest.mark.supports("test_the_walkthroughs_run_moves_in_the_order_the_user_set")
def test_the_skill_may_give_the_result_a_move_due_names() -> None:
    """Given: write's Run, with the move to start no more by `good` due.
    When: may_give asks what write may give.
    Then: it gives `good`."""
    c = d.conversation(d.run(due=(Move("no_more", result="good"),)))
    assert may_give(c, "write", d.ROUTES_OF_WRITE) == ("good",)


@pytest.mark.supports("test_neither_yes_nor_a_change_ends_ups_run_unlaid")
def test_nothing_may_be_given_in_a_run_that_ended() -> None:
    """Given: write's Run, ended, with writer's Start still marked running.
    When: may_give asks what writer may give.
    Then: it gives none."""
    c = d.conversation(d.run(starts=(d.start("writer"),), due=(), ended=True))
    assert may_give(c, "writer", d.ROUTES_OF_WRITE) == ()


# write's Routes with the Route after reviewer's `more` resuming writer, and a Run of them up to
# reviewer's `more`.
RESUMES = (
    *d.ROUTES_OF_WRITE[:2],
    d.route(d.After("result", role="reviewer", result="more"), Move("resume", role="writer")),
)
TO_MORE = (
    CALLED,
    WRITER,
    TIED,
    Gave("r1", "writer", "written", "a01"),
    REVIEWER,
    Tied("r1", "toolu_r", "a02"),
    Gave("r1", "reviewer", "more", "a02"),
)
RESUMED = (Started("r1", "writer", "Mend", {}, "toolu_w2", True), Tied("r1", "toolu_w2", "a01"))


@pytest.mark.supports("test_a_resume_a_route_makes_due_adds_a_start_and_moves_the_run")
def test_a_result_whose_route_resumes_makes_the_resume_due() -> None:
    """Given: reviewer's `more`, whose Route resumes writer.
    When: stand works out the conversation.
    Then: writer's resume is due."""
    (run,) = stand(d.SESSION, TO_MORE, RESUMES).runs
    assert run.due == (Move("resume", role="writer"),)


@pytest.mark.supports("test_a_resume_a_route_makes_due_adds_a_start_and_moves_the_run")
def test_a_resumed_start_takes_its_move_due() -> None:
    """Given: writer's resume due, then writer's Start marked resumed, tied to a01.
    When: stand works out the conversation.
    Then: the Run's last Start is writer's, resumed and tied to a01, with no move due."""
    (run,) = stand(d.SESSION, (*TO_MORE, *RESUMED), RESUMES).runs
    last = run.starts[-1]
    assert (last.role, last.resumed, last.agent_id, last.results) == ("writer", True, "a01", ())
    assert run.due == ()


@pytest.mark.supports("test_a_resume_a_route_makes_due_adds_a_start_and_moves_the_run")
def test_a_resumed_starts_result_makes_its_routes_moves_due() -> None:
    """Given: writer's resumed Start, and its Result `written`.
    When: stand works out the conversation.
    Then: the resumed Start holds `written`, and reviewer's start is due."""
    given = (*TO_MORE, *RESUMED, Gave("r1", "writer", "written", "a01"))
    (run,) = stand(d.SESSION, given, RESUMES).runs
    assert run.starts[-1].results == ("written",)
    assert run.due == START_REVIEWER


@pytest.mark.supports("test_no_kept_results_start_a_new_run")
def test_no_kept_results_pick_up_nothing() -> None:
    """Given: no Kept results.
    When: pick_up reads them for write.
    Then: it gives no Results."""
    assert pick_up(d.ROUTES_OF_WRITE, "write", ()) == ()


@pytest.mark.supports("test_a_new_conversation_picks_up_from_the_kept_results")
def test_kept_results_that_follow_the_routes_are_picked_up() -> None:
    """Given: writer's `written` and reviewer's `more`, which follow write's Routes.
    When: pick_up reads them.
    Then: it gives both Results, in order."""
    kept = (KeptResult("writer", "written"), KeptResult("reviewer", "more"))
    assert pick_up(d.ROUTES_OF_WRITE, "write", kept) == (
        Result("writer", "written"),
        Result("reviewer", "more"),
    )


@pytest.mark.supports("test_kept_results_that_reach_the_end_start_a_new_run")
def test_kept_results_that_reach_a_route_that_starts_no_more_pick_up_nothing() -> None:
    """Given: writer's `written` and reviewer's `good`, whose Route starts no more.
    When: pick_up reads them.
    Then: it gives no Results, as the run starts anew."""
    kept = (KeptResult("writer", "written"), KeptResult("reviewer", "good"))
    assert pick_up(d.ROUTES_OF_WRITE, "write", kept) == ()


@pytest.mark.supports("test_kept_results_off_the_routes_stop_the_command")
def test_kept_results_off_the_routes_are_refused() -> None:
    """Given: reviewer's `good` first, which no Route of write leads to.
    When: pick_up reads it.
    Then: it raises OffRoutes, naming reviewer's `good`."""
    with pytest.raises(OffRoutes, match="good"):
        pick_up(d.ROUTES_OF_WRITE, "write", (KeptResult("reviewer", "good"),))


@pytest.fixture
def plugin(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> str:
    """changelog's folder with the walkthrough's lanes.json, and the system's temporary folder set
    to the case's own."""
    monkeypatch.setenv("TMPDIR", str(tmp_path / "temp"))
    monkeypatch.setattr(tempfile, "tempdir", None)
    os.makedirs(tmp_path / "temp")
    root = tmp_path / "changelog"
    os.makedirs(root / "hooks")
    os.makedirs(root / ".claude-plugin")
    (root / ".claude-plugin" / "plugin.json").write_text('{"name": "changelog"}\n')
    return str(root)


def lay_lanes(plugin: str) -> None:
    """Writes the walkthrough's lanes.json into the plugin."""
    write_lanes(os.path.join(plugin, "hooks", "lanes.json"), d.lanes_file())


@pytest.mark.supports("test_a_result_is_added_for_the_subagents_start")
def test_where_reads_the_conversations_record_and_routes(plugin: str) -> None:
    """Given: changelog's lanes.json, and a run record with write's call.
    When: where reads the conversation for a script.
    Then: it gives write's Run with writer's start due."""
    lay_lanes(plugin)
    add(record_path("changelog", d.SESSION), CALLED)
    (run,) = where(plugin, d.SESSION).runs
    assert run.due == START_WRITER


@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
def test_where_without_lanes_json_is_refused(plugin: str) -> None:
    """Given: changelog with no hooks/lanes.json.
    When: where reads the conversation.
    Then: it raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        where(plugin, d.SESSION)


@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
def test_where_with_a_record_out_of_form_is_refused(plugin: str) -> None:
    """Given: a run record whose line isn't in its form.
    When: where reads the conversation.
    Then: it raises Unreadable."""
    lay_lanes(plugin)
    path = record_path("changelog", d.SESSION)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps({"kind": "nothing"}) + "\n")
    with pytest.raises(Unreadable):
        where(plugin, d.SESSION)
