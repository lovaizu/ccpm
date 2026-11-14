"""The unit tests of the orchestrator's prompt, `skills/up/SKILL.md`, `skills/dn/SKILL.md`,
`skills/ty/SKILL.md`, and `skills/gm/SKILL.md` with `domain/orchestrator.md`: the main
conversation runs alone on Opus, k = 3 times for each case, on invoicer in a throwaway repository
with tree.py real, and each case passes only where all k runs pass, deciding by code each point
that a run's record shows. Each case names the integration case whose orchestrator, played by the
test there, it shows the real orchestrator keeping."""

from __future__ import annotations

import json

import pytest
from rn_example import (
    ALL_DONE,
    ANSWERED,
    HINTS,
    POINT,
    REQUEST,
    TYPED,
    TYPED_TOTALS,
    WITH_POINT,
    invoicer,
)
from rn_prompt_runs import orchestrator_runs

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")

INVOICER = invoicer()
# The walkthrough's run up to its plan put up for the user's sign-off.
TO_THE_PLAN = [f"/rn:up {REQUEST}", "yes", "each file"]
RUN = ".rn/20261114-type-hints-for-invoicer"
SIGNED_OFF = json.dumps(
    [
        {"of": of, "can_do": "", "decisions": [], "words": "", "state": "signed", "issue": ""}
        for of in ("plan", HINTS, TYPED)
    ]
)


def handed_over(readme: str) -> dict[str, str]:
    """A run left with both deliverables done and signed off: the typed totals, the marker, and
    invoicer's README as given, on the run's branch."""
    return {
        f"{RUN}/design-tree.json": json.dumps(ALL_DONE),
        f"{RUN}/sign-offs.json": SIGNED_OFF,
        "invoicer/totals.py": TYPED_TOTALS,
        "invoicer/py.typed": "",
        "README.md": readme,
    }


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


@pytest.mark.supports("test_the_users_ty_signs_off_the_plan_waiting")
def test_the_users_own_ty_on_the_plan_starts_the_hints_generator():
    """Given the plan put up for the user's sign-off
    When the user types `/rn:ty`
    Then on every run the orchestrator calls no rn:ty by the Skill tool, and starts a generator
    whose text names the hints"""
    done = orchestrator_runs(INVOICER, [*TO_THE_PLAN, "/rn:ty"], tree_keeper_wrote(ANSWERED))
    assert not any("rn:ty" in run.skills for run in done)
    assert all(
        any(role == "rn:generator" and HINTS in text for role, text in run.starts) for run in done
    )


@pytest.mark.supports("test_gm_with_what_to_change_sends_the_sign_off_back_and_carries_their_words")
def test_gm_with_words_takes_them_to_the_tree_keeper_and_reads_no_comments():
    """Given the plan put up for the user's sign-off
    When the user types `/rn:gm only the functions that callers import`
    Then on every run the orchestrator runs no `tree.py comments`, and starts or resumes the
    tree-keeper with a text that holds the user's words"""
    words = "only the functions that callers import"
    done = orchestrator_runs(
        INVOICER, [*TO_THE_PLAN, f"/rn:gm {words}"], tree_keeper_wrote(ANSWERED)
    )
    assert not any("tree.py comments" in c for run in done for c in run.commands)
    assert all(
        any(role == "rn:tree-keeper" and words in text for role, text in run.starts + run.resumes)
        for run in done
    )


@pytest.mark.supports("test_gm_alone_has_tree_py_give_the_users_comments_since_the_sign_off")
def test_gm_alone_reads_the_users_comments_on_the_pull_request():
    """Given the plan put up for the user's sign-off
    When the user types `/rn:gm` alone
    Then on every run the orchestrator runs `tree.py comments`"""
    done = orchestrator_runs(INVOICER, [*TO_THE_PLAN, "/rn:gm"], tree_keeper_wrote(ANSWERED))
    assert all(any("tree.py comments" in c for c in run.commands) for run in done)


@pytest.mark.supports(
    "test_ready_marks_the_pull_request_ready_once_every_deliverable_is_signed_off"
)
def test_a_whole_pull_request_that_holds_together_is_marked_ready_with_done():
    """Given a run left with both deliverables done and signed off, and invoicer's README as it was
    When the user types `/rn:up` alone
    Then on every run the orchestrator runs `tree.py ready`, and its last message starts with
    `Done`"""
    left = handed_over(INVOICER["README.md"])
    done = orchestrator_runs(INVOICER, ["/rn:up"], tree_keeper_wrote(ALL_DONE), left=left)
    assert all(any("tree.py ready" in c for c in run.commands) for run in done)
    assert all(run.said[-1].startswith("Done") for run in done)


@pytest.mark.supports(
    "test_a_clash_the_whole_pull_request_read_finds_starts_the_rounds_again_from_its_decision"
)
def test_a_clash_in_the_whole_pull_request_goes_back_to_its_decision_before_ready():
    """Given a run left with both deliverables done and signed off, its README on the branch telling
    callers to pass the tax rate as text where the hints type it Decimal
    When the user types `/rn:up` alone
    Then on no run does the orchestrator run `tree.py ready`, and on every run it starts or resumes
    the tree-keeper with a text naming README.md"""
    readme = INVOICER["README.md"] + '\nPass the tax rate as text, such as `"0.19"`.\n'
    left = handed_over(readme)
    done = orchestrator_runs(INVOICER, ["/rn:up"], tree_keeper_wrote(ALL_DONE), left=left)
    assert not any("tree.py ready" in c for run in done for c in run.commands)
    assert all(
        any(role == "rn:tree-keeper" and "README.md" in t for role, t in run.starts + run.resumes)
        for run in done
    )
