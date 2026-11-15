"""The unit tests of the orchestrator's prompt, `skills/up/SKILL.md`, `skills/dn/SKILL.md`,
`skills/ty/SKILL.md`, and `skills/gm/SKILL.md` with `domain/orchestrator.md`: the main
conversation runs alone on Opus, on invoicer in a throwaway repository with tree.py real, and each
run of a case is a test of its own, deciding by code each point that its record shows, so that the
developer judges the prompt from the results of the case's runs. Each case names the integration
case whose orchestrator, played by the test there, it shows the real orchestrator keeping."""

from __future__ import annotations

import json

import pytest
from rn_example import (
    ALL_DONE,
    ANSWERED,
    HINTS,
    POINT,
    REQUEST,
    SETTLED,
    TYPED,
    TYPED_TOTALS,
    WITH_POINT,
    invoicer,
)
from rn_prompt_runs import RUNS, orchestrator_run

pytestmark = [
    pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt"),
    pytest.mark.parametrize("run", range(RUNS)),
]

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
def test_up_with_a_request_begins_the_run_and_puts_the_goal_to_the_user_as_one_question(run: int):
    """Given invoicer with rn installed
    When the user types `/rn:up` with the walkthrough's request
    Then the orchestrator runs `tree.py begin`, starts the tree-keeper, and its last message drafts
    the goal and ends with one question"""
    got = orchestrator_run(INVOICER, [f"/rn:up {REQUEST}"], run=run)
    assert any("tree.py begin" in c for c in got.commands)
    assert any(role == "rn:tree-keeper" for role, _ in got.starts)
    assert got.said[-1].rstrip().endswith("?") and got.said[-1].count("?") == 1


@pytest.mark.supports(
    "test_up_with_a_request_makes_the_runs_worktree_on_its_branch_with_its_folder"
)
def test_a_near_request_without_the_command_leaves_rn_uncalled(run: int):
    """Given invoicer with rn installed
    When the user asks to fix the typo `totla` in README.md, without `/rn:up`
    Then the main conversation doesn't call rn:up by the Skill tool"""
    got = orchestrator_run(INVOICER, ["Fix the typo `totla` in README.md."], run=run)
    assert "rn:up" not in got.skills


@pytest.mark.supports(
    "test_a_users_point_written_open_keeps_the_deliverable_it_lies_under_from_doing"
)
def test_a_point_the_purpose_leaves_open_goes_to_the_user_with_a_recommendation(run: int):
    """Given the goal confirmed, and the tree-keeper's design tree holding the point on each file
    open
    When the user typed `yes` to the goal
    Then the orchestrator's last message asks that point alone, with `recommend`"""
    got = orchestrator_run(
        INVOICER, [f"/rn:up {REQUEST}", "yes"], tree_keeper_wrote(WITH_POINT), run=run
    )
    assert "each file" in got.said[-1] and "recommend" in got.said[-1].lower()
    assert got.said[-1].count("?") == 1


@pytest.mark.supports(
    "test_a_point_the_best_practice_settles_is_written_by_reasoning_with_no_open_decision_before_it"
)
def test_a_point_the_best_practice_settles_isnt_put_to_the_user(run: int):
    """Given the point on each file answered, and the code best practice settling how the hints are
    checked
    When the run goes on to the plan
    Then the orchestrator doesn't ask the user how the hints are checked"""
    got = orchestrator_run(
        INVOICER, [f"/rn:up {REQUEST}", "yes", "each file"], tree_keeper_wrote(ANSWERED), run=run
    )
    assert not any("mypy" in said and "?" in said for said in got.said)
    assert POINT not in got.said[-1]


@pytest.mark.supports("test_runs_with_no_run_left_lists_none")
def test_up_alone_with_no_run_says_it_has_none_to_pick_up(run: int):
    """Given invoicer with no run of rn
    When the user types `/rn:up` alone
    Then the orchestrator runs `tree.py runs`, starts no role, and says it has no run to pick up"""
    got = orchestrator_run(INVOICER, ["/rn:up"], run=run)
    assert any("tree.py runs" in c for c in got.commands) and not got.starts
    assert "no run" in got.said[-1].lower()


@pytest.mark.supports("test_pause_commits_the_work_so_far_with_each_roles_step_and_pushes_it")
def test_dn_pauses_with_the_work_pushed_and_says_paused(run: int):
    """Given a run making the hints
    When the user types `/rn:dn`
    Then the orchestrator runs `tree.py pause`, and its last message starts with `Paused`"""
    got = orchestrator_run(
        INVOICER,
        [f"/rn:up {REQUEST}", "yes", "each file", "/rn:dn"],
        tree_keeper_wrote(ANSWERED),
        run=run,
    )
    assert any("tree.py pause" in c for c in got.commands)
    assert got.said[-1].startswith("Paused")


@pytest.mark.supports("test_the_orchestrator_cant_approve_for_the_user_by_the_skill_tool")
def test_the_orchestrator_waits_for_the_users_ty_and_never_calls_it(run: int):
    """Given the plan put up for the user's sign-off
    When the user says nothing more
    Then the orchestrator doesn't call rn:ty by the Skill tool or start a generator"""
    got = orchestrator_run(
        INVOICER, [f"/rn:up {REQUEST}", "yes", "each file"], tree_keeper_wrote(ANSWERED), run=run
    )
    assert "rn:ty" not in got.skills
    assert not any(role == "rn:generator" for role, _ in got.starts)


@pytest.mark.supports(
    "test_a_more_the_people_fall_short_by_changes_its_decision_and_reaches_the_next_round"
)
def test_a_more_the_people_would_never_meet_changes_no_decision(run: int):
    """Given the hints' round judged, an evaluator naming only that the hints of a private helper
    use `Any`
    When the orchestrator judges the `more`
    Then it doesn't run `tree.py more`"""
    answers = {
        "good": [],
        "more": [{"question": "N2", "good_when": "A private helper's hints use Any."}],
    }
    results = {**tree_keeper_wrote(ANSWERED), "evaluator": {"result": "done", "answers": answers}}
    got = orchestrator_run(
        INVOICER, [f"/rn:up {REQUEST}", "yes", "each file", "/rn:ty"], results, run=run
    )
    assert not any("tree.py more" in c for c in got.commands)


@pytest.mark.supports(
    "test_a_more_the_people_fall_short_by_changes_its_decision_and_reaches_the_next_round"
)
def test_a_more_the_people_fall_short_by_goes_back_to_the_decision_it_changes(run: int):
    """Given the hints' round judged, an evaluator putting N2 in more, as a caller can't tell the
    rate that `total` takes
    When the orchestrator judges the `more`
    Then it resumes or starts the tree-keeper with a text naming N2, as the people fall short by
    it, so that with the case above it picks each `more` they fall short by and no other"""
    answers = {
        "good": [],
        "more": [{"question": "N2", "good_when": "A caller's editor shows the type of each rate."}],
    }
    results = {**tree_keeper_wrote(ANSWERED), "evaluator": {"result": "done", "answers": answers}}
    got = orchestrator_run(
        INVOICER, [f"/rn:up {REQUEST}", "yes", "each file", "/rn:ty"], results, run=run
    )
    assert any(role == "rn:tree-keeper" and "N2" in t for role, t in got.starts + got.resumes)


@pytest.mark.supports("test_the_users_ty_signs_off_the_plan_waiting")
def test_the_users_own_ty_on_the_plan_starts_the_hints_generator(run: int):
    """Given the plan put up for the user's sign-off
    When the user types `/rn:ty`
    Then the orchestrator calls no rn:ty by the Skill tool, and starts a generator whose text names
    the hints"""
    got = orchestrator_run(INVOICER, [*TO_THE_PLAN, "/rn:ty"], tree_keeper_wrote(ANSWERED), run=run)
    assert "rn:ty" not in got.skills
    assert any(role == "rn:generator" and HINTS in text for role, text in got.starts)


@pytest.mark.supports("test_gm_with_what_to_change_sends_the_sign_off_back_and_carries_their_words")
def test_gm_with_words_takes_them_to_the_tree_keeper_and_reads_no_comments(run: int):
    """Given the plan put up for the user's sign-off
    When the user types `/rn:gm only the functions that callers import`
    Then the orchestrator runs no `tree.py comments`, and starts or resumes the tree-keeper with a
    text that holds the user's words"""
    words = "only the functions that callers import"
    got = orchestrator_run(
        INVOICER, [*TO_THE_PLAN, f"/rn:gm {words}"], tree_keeper_wrote(ANSWERED), run=run
    )
    assert not any("tree.py comments" in c for c in got.commands)
    assert any(
        role == "rn:tree-keeper" and words in text for role, text in got.starts + got.resumes
    )


@pytest.mark.supports("test_gm_alone_has_tree_py_give_the_users_comments_since_the_sign_off")
def test_gm_alone_reads_the_users_comments_on_the_pull_request(run: int):
    """Given the plan put up for the user's sign-off
    When the user types `/rn:gm` alone
    Then the orchestrator runs `tree.py comments`"""
    got = orchestrator_run(INVOICER, [*TO_THE_PLAN, "/rn:gm"], tree_keeper_wrote(ANSWERED), run=run)
    assert any("tree.py comments" in c for c in got.commands)


@pytest.mark.supports(
    "test_the_orchestrator_gets_the_round_and_puts_up_the_points_the_generator_settled"
)
def test_a_deliverables_sign_off_lists_the_points_its_generator_settled(run: int):
    """Given a run left with the plan signed off, and the hints' round 1 done: what its generator
    made naming the point on amounts it settled without asking, and each group's Answers good
    When the user types `/rn:up` alone
    Then the orchestrator puts the hints up with the Decimal point among the decisions taken
    without asking"""
    rounds = f"{RUN}/rounds/invoicer--/1"
    made = {
        "decisions": [{"about": POINT, "where": "invoicer/"}],
        "more": [],
        "settled": [SETTLED],
    }
    met = {
        group: {"good": [{"question": n, "lines": ["invoicer/totals.py:1"]} for n in ids]}
        for group, ids in (
            ("C1", ("N1", "N2", "N3")),
            ("C2", ("N4", "N5", "N6", "N7")),
            ("C3", ("N8",)),
        )
    }
    left = {
        f"{RUN}/design-tree.json": json.dumps(ANSWERED),
        f"{RUN}/sign-offs.json": json.dumps(
            [
                {
                    "of": "plan",
                    "can_do": "",
                    "decisions": [],
                    "words": "",
                    "state": "signed",
                    "issue": "",
                }
            ]
        ),
        "invoicer/totals.py": TYPED_TOTALS,
        f"{rounds}/made.json": json.dumps(made),
        **{
            f"{rounds}/answers-{group}.json": json.dumps(dict(each, more=[]))
            for group, each in met.items()
        },
    }
    got = orchestrator_run(INVOICER, ["/rn:up"], tree_keeper_wrote(ANSWERED), left=left, run=run)
    put_up = json.loads(got.files[f"{RUN}/sign-offs.json"])
    assert any(
        each["of"] == HINTS and any("Decimal" in d for d in each["decisions"]) for each in put_up
    )


@pytest.mark.supports(
    "test_ready_marks_the_pull_request_ready_once_every_deliverable_is_signed_off"
)
def test_a_whole_pull_request_that_holds_together_is_marked_ready_with_done(run: int):
    """Given a run left with both deliverables done and signed off, and invoicer's README as it was
    When the user types `/rn:up` alone
    Then the orchestrator runs `tree.py ready`, and its last message starts with `Done`"""
    left = handed_over(INVOICER["README.md"])
    got = orchestrator_run(INVOICER, ["/rn:up"], tree_keeper_wrote(ALL_DONE), left=left, run=run)
    assert any("tree.py ready" in c for c in got.commands)
    assert got.said[-1].startswith("Done")


@pytest.mark.supports(
    "test_a_clash_the_whole_pull_request_read_finds_starts_the_rounds_again_from_its_decision"
)
def test_a_clash_in_the_whole_pull_request_goes_back_to_its_decision_before_ready(run: int):
    """Given a run left with both deliverables done and signed off, its README on the branch telling
    callers to pass the tax rate as text where the hints type it Decimal
    When the user types `/rn:up` alone
    Then the orchestrator doesn't run `tree.py ready`, and starts or resumes the tree-keeper with a
    text naming README.md"""
    readme = INVOICER["README.md"] + '\nPass the tax rate as text, such as `"0.19"`.\n'
    left = handed_over(readme)
    got = orchestrator_run(INVOICER, ["/rn:up"], tree_keeper_wrote(ALL_DONE), left=left, run=run)
    assert not any("tree.py ready" in c for c in got.commands)
    assert any(
        role == "rn:tree-keeper" and "README.md" in t for role, t in got.starts + got.resumes
    )


@pytest.mark.supports(
    "test_a_clash_the_whole_pull_request_read_finds_starts_the_rounds_again_from_its_decision"
)
def test_a_part_beyond_the_goal_in_the_whole_pull_request_goes_back_to_its_decision_before_ready(
    run: int,
):
    """Given a run left with both deliverables done and signed off, its branch holding besides
    invoicer/cli.py, a command line that the goal doesn't need
    When the user types `/rn:up` alone
    Then the orchestrator doesn't run `tree.py ready`, and starts or resumes the tree-keeper with a
    text naming cli.py"""
    cli = "import sys\n\nprint(sys.argv)\n"
    left = {**handed_over(INVOICER["README.md"]), "invoicer/cli.py": cli}
    got = orchestrator_run(INVOICER, ["/rn:up"], tree_keeper_wrote(ALL_DONE), left=left, run=run)
    assert not any("tree.py ready" in c for c in got.commands)
    assert any(role == "rn:tree-keeper" and "cli.py" in t for role, t in got.starts + got.resumes)


@pytest.mark.supports(
    "test_a_clash_the_whole_pull_request_read_finds_starts_the_rounds_again_from_its_decision"
)
def test_a_file_that_names_what_invoicer_doesnt_have_goes_back_to_its_decision_before_ready(
    run: int,
):
    """Given a run left with both deliverables done and signed off, its README on the branch naming
    `invoicer.compute_total`, a name that invoicer doesn't have, as its function is `total`
    When the user types `/rn:up` alone
    Then the orchestrator doesn't run `tree.py ready`, and starts or resumes the tree-keeper with a
    text naming README.md"""
    readme = INVOICER["README.md"] + "\nCall `invoicer.compute_total(lines, rate)` for the total.\n"
    left = handed_over(readme)
    got = orchestrator_run(INVOICER, ["/rn:up"], tree_keeper_wrote(ALL_DONE), left=left, run=run)
    assert not any("tree.py ready" in c for c in got.commands)
    assert any(
        role == "rn:tree-keeper" and "README.md" in t for role, t in got.starts + got.resumes
    )
