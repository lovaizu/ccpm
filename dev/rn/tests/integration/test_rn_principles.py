"""The integration cases of rn's principles: for each, a case where the parts keep it and, where a
role can break it, a case where one does and a part stops it. Each takes the fixture `broken`,
which takes out of the installed rn the part that holds its principle where TRACE_BROKEN is 1, so
that trace.py sees the case fail without that part."""

from __future__ import annotations

import json
import os

import pytest
from claude_code import Conversation
from rn_example import (
    ANSWERED,
    HINTS,
    POINT,
    TYPED,
    Repo,
    Run,
    condition,
    decided,
    git,
    gives,
    keeper_writes,
    plan,
    records_all,
    started,
    text_of,
    throwaway,
    tree,
    write,
)

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")

TYPED_ONLY = decided("Where the marker lies", "invoicer/py.typed, empty", "reasoning")


def hints_doing(conv: Conversation, repo: Repo, run: Run, design: dict = ANSWERED) -> None:
    """The design tree written, and the plan signed off by the user's /rn:ty, so the hints are
    doing."""
    _, keeper = started(conv, repo, run, "tree-keeper")
    keeper_writes(keeper, repo, run, design, "The plan.")
    path = os.path.join(repo.temp, "plan.json")
    conv.write(None, path, json.dumps({"of": "plan", "can_do": "", "decisions": [], "words": ""}))
    conv.bash(tree(repo, "sign-off", run.folder, path))
    conv.type("/rn:ty")
    keeper_writes(keeper, repo, run, design, "The user signed the plan off.")


@pytest.mark.supports("Drawn out along the design tree", "Cut", "tree.py")
def test_a_generators_cut_holds_its_deliverables_decisions_and_no_others(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given the plan signed off, the typed marker holding a decision of its own
    When the orchestrator cuts the generator's cut of the hints
    Then the cut holds the hints' decision, and not the typed marker's"""
    design = plan(condition("N3", decided(POINT, "each file", "user")))
    design["deliverables"][1]["necessary_conditions"][0]["decisions"] = [TYPED_ONLY]
    hints_doing(conv, repo, run, design)
    given, _ = started(conv, repo, run, "generator", HINTS)
    held = json.loads(text_of(os.path.join(run.worktree, given["cut"])))
    assert [each["about"] for each in held["decisions"]] == [POINT]


@pytest.mark.supports("Drawn out along the design tree", "guard", "generator")
def test_a_generator_that_reads_the_whole_design_tree_is_stopped(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running
    When it reads the run's design-tree.json
    Then the guard stops the read"""
    hints_doing(conv, repo, run)
    _, generator = started(conv, repo, run, "generator", HINTS)
    read = generator.read(os.path.join(run.worktree, run.folder, "design-tree.json"))
    assert read.blocked


@pytest.mark.supports("Every step by best practice", "guard", "generator")
def test_a_generator_whose_record_skips_the_practices_of_its_best_practice_is_held_at_its_end(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running, which recorded each step of its part and no practice
    of the code best practice
    When it gives `done`
    Then the guard holds its end, naming a practice of the code best practice it left out"""
    hints_doing(conv, repo, run)
    given, generator = started(conv, repo, run, "generator", HINTS)
    records_all(generator, repo, given, "generator")
    stopped, reached = gives(generator, repo, "generator", "done")
    assert stopped.blocked and reached is None and "N1.1" in stopped.said


@pytest.mark.supports("Every step by best practice", "guard", "generator", "Cut")
def test_a_generator_whose_record_skips_its_refactor_practices_is_held_at_its_end(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running, which recorded each step of its part and each practice
    of the code best practice, and no practice of the refactor-code best practice that its cut names
    When it gives `done`
    Then the guard holds its end, naming the refactor-code best practice"""
    hints_doing(conv, repo, run)
    given, generator = started(conv, repo, run, "generator", HINTS)
    records_all(generator, repo, given, "generator", "code")
    stopped, reached = gives(generator, repo, "generator", "done")
    assert stopped.blocked and reached is None and "refactor-code" in stopped.said


@pytest.mark.supports("Every step by best practice", "guard", "generator")
def test_a_generator_whose_record_holds_each_step_and_practice_ends_with_its_result_kept(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running, which recorded each step and each practice of the code
    and refactor-code best practices, and wrote what it made naming each decision of its cut
    When it gives `done`
    Then the guard lets its end through, and its record keeps `done`"""
    hints_doing(conv, repo, run)
    given, generator = started(conv, repo, run, "generator", HINTS)
    records_all(generator, repo, given, "generator", "code", "refactor-code")
    made = {"decisions": [{"about": POINT, "where": "invoicer/"}], "more": [], "settled": []}
    write(run.worktree, given["made"], json.dumps(made))
    stopped, reached = gives(generator, repo, "generator", "done")
    assert not stopped.blocked and reached
    assert json.loads(text_of(os.path.join(run.worktree, given["record"])))["result"] == "done"


@pytest.mark.supports("Every item handled", "guard", "generator", "Cut")
def test_a_generator_whose_made_leaves_out_a_decision_of_its_cut_is_held_at_its_end(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running, which recorded each step and practice, and wrote what it
    made naming none of its cut's decisions
    When it gives `done`
    Then the guard holds its end, naming the decision it left out"""
    hints_doing(conv, repo, run)
    given, generator = started(conv, repo, run, "generator", HINTS)
    records_all(generator, repo, given, "generator", "code", "refactor-code")
    write(run.worktree, given["made"], json.dumps({"decisions": [], "more": [], "settled": []}))
    stopped, _ = gives(generator, repo, "generator", "done")
    assert stopped.blocked and POINT in stopped.said


@pytest.mark.supports("Every item handled", "guard", "evaluator", "Necessary condition")
def test_an_evaluator_whose_answers_leave_a_condition_of_its_group_is_held_at_its_end(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given an evaluator of the hints' group C3 running, which recorded each step
    When it writes Answers with no answer at all, and gives `done`
    Then the guard holds its end, naming N8, the condition of C3"""
    hints_doing(conv, repo, run)
    given, evaluator = started(conv, repo, run, "evaluator", HINTS, "C3")
    records_all(evaluator, repo, given, "evaluator")
    write(run.worktree, given["answers"], json.dumps({"good": [], "more": []}))
    stopped, _ = gives(evaluator, repo, "evaluator", "done")
    assert stopped.blocked and "N8" in stopped.said


@pytest.mark.supports("Judged by the people it's for", "guard", "evaluator")
def test_an_evaluator_that_reads_the_generators_cut_is_stopped(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator started, and an evaluator of the hints' group C1 running
    When the evaluator reads the generator's cut
    Then the guard stops the read, as the deliverable's people never see what its maker meant"""
    hints_doing(conv, repo, run)
    made, _ = started(conv, repo, run, "generator", HINTS)
    _, evaluator = started(conv, repo, run, "evaluator", HINTS, "C1")
    assert evaluator.read(os.path.join(run.worktree, made["cut"])).blocked


@pytest.mark.supports("Judged by the people it's for", "guard", "evaluator", "Deliverable")
def test_an_evaluator_reads_the_deliverable_its_people_have(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given an evaluator of the hints' group C1 running
    When it reads invoicer/totals.py of the deliverable, and the run's design-tree.json
    Then the guard lets the first read through and stops the second"""
    hints_doing(conv, repo, run)
    _, evaluator = started(conv, repo, run, "evaluator", HINTS, "C1")
    assert not evaluator.read(os.path.join(run.worktree, "invoicer", "totals.py")).blocked
    assert evaluator.read(os.path.join(run.worktree, run.folder, "design-tree.json")).blocked


@pytest.mark.supports("Signed off before it's built on", "tree.py", "Sign-off")
def test_no_deliverable_is_marked_doing_before_the_plan_is_signed_off(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given the plan written with its point answered, put up, and not yet signed off
    When the tree-keeper writes the tree again
    Then tree.py marks no deliverable doing"""
    _, keeper = started(conv, repo, run, "tree-keeper")
    keeper_writes(keeper, repo, run, ANSWERED, "The user answered each file.")
    path = os.path.join(repo.temp, "plan.json")
    conv.write(None, path, json.dumps({"of": "plan", "can_do": "", "decisions": [], "words": ""}))
    conv.bash(tree(repo, "sign-off", run.folder, path))
    wrote = keeper_writes(keeper, repo, run, ANSWERED, "Again.")
    assert wrote.exit_code == 0 and json.loads(wrote.output)["doing"] == []


@pytest.mark.supports("Signed off before it's built on", "guard", "orchestrator")
def test_the_orchestrator_cant_start_the_typed_markers_generator_before_the_hints_are_signed_off(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given the plan signed off and the hints doing, the typed marker waiting on the hints'
    sign-off
    When the main conversation starts a generator of the typed marker
    Then the guard stops the start, as no start of it is due before the user's /rn:ty"""
    hints_doing(conv, repo, run)
    started_answer, agent = conv.start(
        "rn:generator", json.dumps({"deliverable": TYPED, "run": run.folder}), "generator"
    )
    assert agent is None and started_answer.blocked


@pytest.mark.supports("Back to the design tree on a problem", "More kept", "Decision", "Cut")
def test_the_next_round_is_made_from_the_decision_changed_and_the_more_kept(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' round 1 judged, with a `more` the people fall short by
    When the tree-keeper writes the decision it changes and keeps the `more`
    Then the generator's cut of round 2 holds the decision and the More kept, so that the round
    makes the deliverable from the design"""
    hints_doing(conv, repo, run)
    started(conv, repo, run, "generator", HINTS)
    _, keeper = started(conv, repo, run, "tree-keeper")
    rate = decided("How a rate is typed", "a Decimal named Rate", "maker")
    changed = plan(condition("N3", decided(POINT, "each file", "user")), condition("N2", rate))
    keeper_writes(keeper, repo, run, changed, "A rate reads apart from an amount.")
    keeper.bash(tree(repo, "more", run.folder, HINTS, "N2", "A caller tells a rate by its type."))
    given, _ = started(conv, repo, run, "generator", HINTS)
    held = json.loads(text_of(os.path.join(run.worktree, given["cut"])))
    assert rate in held["decisions"]
    assert [each["condition"] for each in held["more"]] == ["N2"]


@pytest.mark.supports(
    "Back to the design tree on a problem", "S1", "tree.py", "More kept", "Necessary condition"
)
def test_a_more_kept_with_no_change_to_a_decision_of_its_condition_is_refused(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' round 1 judged, with a `more` under N2 that the people fall short by, and no
    decision of N2 changed since the round's cut
    When the tree-keeper keeps the `more`
    Then tree.py exits 1, naming N2, and the generator's cut of round 2 holds no More kept, as the
    round would make it good by a fix beside the design"""
    hints_doing(conv, repo, run)
    started(conv, repo, run, "generator", HINTS)
    _, keeper = started(conv, repo, run, "tree-keeper")
    kept = keeper.bash(
        tree(repo, "more", run.folder, HINTS, "N2", "A caller tells a rate by its type.")
    )
    given, _ = started(conv, repo, run, "generator", HINTS)
    held = json.loads(text_of(os.path.join(run.worktree, given["cut"])))
    assert kept.exit_code == 1 and "N2" in kept.output and held["more"] == []


@pytest.mark.supports("The design tree revised on each run", "Best practice", "Cut")
def test_a_best_practice_made_on_a_run_is_taken_over_rns_own_of_its_kind(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given a best practice of the kind code made on an earlier run, in .rn/best-practices/code/
    of the run's worktree
    When the orchestrator cuts an evaluator's cut of the hints
    Then its best practice is the one made on the run"""
    hints_doing(conv, repo, run)
    own = os.path.join(repo.plugin, "domain", "best-practices", "code", "best-practice.json")
    made = write(run.worktree, ".rn/best-practices/code/best-practice.json", text_of(own))
    given, _ = started(conv, repo, run, "evaluator", HINTS, "C1")
    assert os.path.join(run.worktree, given["best_practice"]) == made


@pytest.mark.supports("The design tree revised on each run", "guard", "generator", "Best practice")
def test_a_generator_that_writes_a_best_practice_is_stopped(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running
    When it writes .rn/best-practices/code/best-practice.json in the run's worktree
    Then the guard stops the write, as a best practice changes only as a deliverable that the user
    took at Done"""
    hints_doing(conv, repo, run)
    _, generator = started(conv, repo, run, "generator", HINTS)
    path = os.path.join(run.worktree, ".rn", "best-practices", "code", "best-practice.json")
    wrote = generator.write(path, "{}")
    assert wrote.blocked and not os.path.exists(path)


@pytest.mark.supports("Tried in a throwaway copy", "throwaway.py", "Try record")
def test_a_try_changes_no_file_of_the_worktree_nor_of_the_users_home(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running
    When it tries `touch made-by-try && touch "$HOME/made-by-try"` by throwaway.py
    Then the try gives 0, and neither the worktree nor the user's home holds made-by-try"""
    hints_doing(conv, repo, run)
    _, generator = started(conv, repo, run, "generator", HINTS)
    command = 'touch made-by-try && touch "$HOME/made-by-try"'
    tried = generator.bash(throwaway(repo, "try", run.folder, HINTS, "1", command))
    assert tried.exit_code == 0
    assert not os.path.exists(os.path.join(run.worktree, "made-by-try"))
    assert not os.path.exists(os.path.join(os.path.expanduser("~"), "made-by-try"))


@pytest.mark.supports("Tried in a throwaway copy", "guard", "generator")
def test_a_generator_that_runs_the_deliverables_command_in_the_worktree_is_stopped(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running
    When it runs `python3 -m pytest -q` in the worktree
    Then the guard stops it, naming throwaway.py"""
    hints_doing(conv, repo, run)
    _, generator = started(conv, repo, run, "generator", HINTS)
    stopped = generator.bash("python3 -m pytest -q")
    assert stopped.blocked and "throwaway.py" in stopped.said


@pytest.mark.supports("The repository holds the work", "tree.py", "Place")
def test_each_step_of_the_generator_leaves_its_work_committed(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running, which wrote invoicer/lines.py
    When it keeps its Place at step 4
    Then the worktree has nothing left uncommitted"""
    hints_doing(conv, repo, run)
    _, generator = started(conv, repo, run, "generator", HINTS)
    generator.write(os.path.join(run.worktree, "invoicer", "lines.py"), "class Line: ...\n")
    generator.bash(tree(repo, "place", run.folder, HINTS, "generator", "4"))
    assert git(run.worktree, "status", "--porcelain") == ""


@pytest.mark.supports("The repository holds the work", "guard", "generator")
def test_a_generator_that_writes_in_the_users_checkout_is_stopped(
    broken: bool, conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running in the run's worktree
    When it writes invoicer/lines.py in the user's own checkout
    Then the guard stops the write, and the checkout is left as it was"""
    hints_doing(conv, repo, run)
    _, generator = started(conv, repo, run, "generator", HINTS)
    wrote = generator.write(os.path.join(repo.root, "invoicer", "lines.py"), "class Line: ...\n")
    assert wrote.blocked and git(repo.root, "status", "--porcelain") == ""
