"""The unit tests of the orchestrator's prompt, `skills/up/SKILL.md`, `skills/dn/SKILL.md`,
`skills/ty/SKILL.md`, and `skills/gm/SKILL.md` with `domain/orchestrator.md`: the main
conversation runs alone on Opus, k = 3 times for each case, on invoicer in a throwaway repository
with tree.py real, and each case passes only where all k runs pass, deciding by code each point
that a run's record shows. Each case names the integration case whose orchestrator, played by the
test there, it shows the real orchestrator keeping."""

from __future__ import annotations

import pytest
from rn_example import ANSWERED, POINT, REQUEST, WITH_POINT, invoicer
from rn_prompt_runs import orchestrator_runs

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")

INVOICER = invoicer()


def tree_keeper_wrote(design: dict) -> dict[str, dict]:
    """The tree-keeper's result: `done`, with the design tree it wrote."""
    return {"tree-keeper": {"result": "done", "reply": "Wrote the tree.", "tree": design}}


@pytest.mark.supports(
    "test_up_with_a_request_makes_the_runs_worktree_on_its_branch_with_its_folder"
)
def test_up_with_a_request_begins_the_run_and_puts_the_goal_to_the_user_as_one_question():
    """Given invoicer with rn installed
    When the user types `/rn:up` with the walkthrough's request
    Then on every run the orchestrator runs `tree.py begin`, starts the tree-keeper, and its last
    message drafts the goal and ends with one question"""
    done = orchestrator_runs(INVOICER, [f"/rn:up {REQUEST}"])
    assert all(any("tree.py begin" in c for c in run.commands) for run in done)
    assert all(any(role == "rn:tree-keeper" for role, _ in run.starts) for run in done)
    assert all(run.said[-1].rstrip().endswith("?") and run.said[-1].count("?") == 1 for run in done)


@pytest.mark.supports(
    "test_up_with_a_request_makes_the_runs_worktree_on_its_branch_with_its_folder"
)
def test_a_near_request_without_the_command_leaves_rn_uncalled():
    """Given invoicer with rn installed
    When the user asks to fix the typo `totla` in README.md, without `/rn:up`
    Then on no run does the main conversation call rn:up by the Skill tool"""
    done = orchestrator_runs(INVOICER, ["Fix the typo `totla` in README.md."])
    assert not any("rn:up" in run.skills for run in done)


@pytest.mark.supports(
    "test_a_users_point_written_open_keeps_the_deliverable_it_lies_under_from_doing"
)
def test_a_point_the_purpose_leaves_open_goes_to_the_user_with_a_recommendation():
    """Given the goal confirmed, and the tree-keeper's design tree holding the point on each file
    open
    When the user typed `yes` to the goal
    Then on every run the orchestrator's last message asks that point alone, with `recommend`"""
    done = orchestrator_runs(INVOICER, [f"/rn:up {REQUEST}", "yes"], tree_keeper_wrote(WITH_POINT))
    assert all("each file" in run.said[-1] and "recommend" in run.said[-1].lower() for run in done)
    assert all(run.said[-1].count("?") == 1 for run in done)


@pytest.mark.supports(
    "test_a_point_the_best_practice_settles_is_written_by_reasoning_with_no_open_decision_before_it"
)
def test_a_point_the_best_practice_settles_isnt_put_to_the_user():
    """Given the point on each file answered, and the code best practice settling how the hints are
    checked
    When the run goes on to the plan
    Then on no run does the orchestrator ask the user how the hints are checked"""
    done = orchestrator_runs(
        INVOICER, [f"/rn:up {REQUEST}", "yes", "each file"], tree_keeper_wrote(ANSWERED)
    )
    assert not any("mypy" in said and "?" in said for run in done for said in run.said)
    assert all(POINT not in run.said[-1] for run in done)


@pytest.mark.supports("test_runs_with_no_run_left_lists_none")
def test_up_alone_with_no_run_says_it_has_none_to_pick_up():
    """Given invoicer with no run of rn
    When the user types `/rn:up` alone
    Then on every run the orchestrator runs `tree.py runs`, starts no role, and says it has no run
    to pick up"""
    done = orchestrator_runs(INVOICER, ["/rn:up"])
    assert all(any("tree.py runs" in c for c in run.commands) and not run.starts for run in done)
    assert all("no run" in run.said[-1].lower() for run in done)


@pytest.mark.supports("test_pause_commits_the_work_so_far_with_each_roles_step_and_pushes_it")
def test_dn_pauses_with_the_work_pushed_and_says_paused():
    """Given a run making the hints
    When the user types `/rn:dn`
    Then on every run the orchestrator runs `tree.py pause`, and its last message starts with
    `Paused`"""
    done = orchestrator_runs(
        INVOICER, [f"/rn:up {REQUEST}", "yes", "each file", "/rn:dn"], tree_keeper_wrote(ANSWERED)
    )
    assert all(any("tree.py pause" in c for c in run.commands) for run in done)
    assert all(run.said[-1].startswith("Paused") for run in done)


@pytest.mark.supports("test_the_orchestrator_cant_approve_for_the_user_by_the_skill_tool")
def test_the_orchestrator_waits_for_the_users_ty_and_never_calls_it():
    """Given the plan put up for the user's sign-off
    When the user says nothing more
    Then on no run does the orchestrator call rn:ty by the Skill tool or start a generator"""
    done = orchestrator_runs(
        INVOICER, [f"/rn:up {REQUEST}", "yes", "each file"], tree_keeper_wrote(ANSWERED)
    )
    assert not any("rn:ty" in run.skills for run in done)
    assert not any(role == "rn:generator" for run in done for role, _ in run.starts)


@pytest.mark.supports(
    "test_a_lack_the_people_fall_short_by_changes_its_decision_and_reaches_the_next_round"
)
def test_a_lack_the_people_would_never_meet_changes_no_decision():
    """Given the hints' round judged, an evaluator naming only that the hints of a private helper
    use `Any`
    When the orchestrator judges the lack
    Then on no run does it run `tree.py lack`"""
    answers = {
        "met": [],
        "not_met": [{"question": "N2", "lacks": "A private helper's hints use Any."}],
    }
    results = {**tree_keeper_wrote(ANSWERED), "evaluator": {"result": "done", "answers": answers}}
    done = orchestrator_runs(INVOICER, [f"/rn:up {REQUEST}", "yes", "each file", "/rn:ty"], results)
    assert not any("tree.py lack" in c for run in done for c in run.commands)
