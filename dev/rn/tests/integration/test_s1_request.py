"""The integration cases of S1, a request and a deliverable made in rounds: the user types `/rn:up`
with what they want, tree.py makes the run's worktree, the tree-keeper writes the goal and the
plan, and each deliverable whose turn has come is made by a generator, tried in a throwaway copy,
and judged by an evaluator for each group of its necessary conditions, round after round. The test
plays the user, the orchestrator, and each role."""

from __future__ import annotations

import json
import os

import pytest
from claude_code import Conversation
from rn_example import (
    ANSWERED,
    CODE_GROUPS,
    HINTS,
    POINT,
    TYPED,
    WITH_POINT,
    WORDS,
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


def signed_plan(conv: Conversation, repo: Repo, run: Run) -> None:
    """The plan of the walkthrough, its point answered, put up and signed off by the user's
    /rn:ty, and the tree-keeper's write of the sign-off, which marks the hints doing."""
    _, keeper = started(conv, repo, run, "tree-keeper")
    keeper_writes(keeper, repo, run, ANSWERED, "The user answered each file.")
    put_up(conv, repo, run, "plan")
    conv.type("/rn:ty")
    keeper_writes(keeper, repo, run, ANSWERED, "The user signed the plan off.")


def put_up(conv: Conversation, repo: Repo, run: Run, of: str) -> None:
    """The orchestrator puts the plan or the deliverable at the path up for the user's sign-off."""
    path = os.path.join(repo.temp, f"sign-off-{len(os.listdir(repo.temp))}.json")
    sign_off = {"of": of, "can_do": "", "decisions": [], "words": ""}
    conv.write(None, path, json.dumps(sign_off))
    done = conv.bash(tree(repo, "sign-off", run.folder, path))
    assert done.exit_code == 0, done.output


@pytest.mark.supports("S1", "orchestrator", "tree.py")
def test_up_with_a_request_makes_the_runs_worktree_on_its_branch_with_its_folder(
    conv: Conversation, repo: Repo
):
    """Given the repository of invoicer with rn installed
    When the user types `/rn:up` with the walkthrough's request, and the orchestrator runs
    `tree.py begin type hints for invoicer`
    Then tree.py prints a worktree under .claude/worktrees/ on the branch rn/<run>, whose .rn/<run>/
    holds records/ and rounds/, committed, and the user's checkout is left as it was"""
    conv.type("/rn:up type hints for invoicer, so that the people who call it see each type")
    made = conv.bash(tree(repo, "begin", WORDS))
    worktree = made.output.strip()
    name = os.path.basename(worktree).removeprefix("rn-")
    assert made.exit_code == 0 and name.endswith("-type-hints-for-invoicer")
    assert worktree == os.path.join(repo.root, ".claude", "worktrees", f"rn-{name}")
    assert git(worktree, "branch", "--show-current").strip() == f"rn/{name}"
    assert git(worktree, "status", "--porcelain") == ""
    assert os.path.isdir(os.path.join(worktree, ".rn", name, "records"))
    assert git(repo.root, "status", "--porcelain") == ""


@pytest.mark.supports("S1", "tree.py")
def test_begin_refuses_a_run_that_already_has_its_worktree(
    conv: Conversation, repo: Repo, run: Run
):
    """Given a run begun on the walkthrough's request today
    When the orchestrator runs `tree.py begin type hints for invoicer` again
    Then tree.py exits 1 naming the run's worktree, and makes nothing"""
    again = conv.bash(tree(repo, "begin", WORDS))
    assert again.exit_code == 1 and run.worktree in again.output
    assert len(git(repo.root, "worktree", "list").splitlines()) == 2


@pytest.mark.supports("S1", "tree-keeper", "Cut", "adapters")
def test_the_tree_keeper_starts_with_its_cut_of_the_run_alone(
    conv: Conversation, repo: Repo, run: Run
):
    """Given a run begun, with no design tree yet
    When the orchestrator has tree.py cut the tree-keeper's cut, and starts it with its run values
    Then the run values name its record, the run, and the run's design-tree.json, and the guard
    lets the start through"""
    given, keeper = started(conv, repo, run, "tree-keeper")
    assert given["run"] == run.folder
    assert given["tree"] == os.path.join(run.folder, "design-tree.json")
    assert given["record"].startswith(os.path.join(run.folder, "records", ""))
    assert keeper.running


@pytest.mark.supports("S1", "tree-keeper", "Design tree", "Decision", "Point")
def test_the_goal_and_the_plan_written_commit_the_design_tree_with_the_point_open(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the tree-keeper started, and the user confirmed the goal
    When it writes the goal and the walkthrough's plan, with the point on each file open, by
    `tree.py write` with its ground
    Then tree.py exits 0, prints the goal and both deliverables as changed and none doing, and
    the design tree it committed holds the point with `decided` null"""
    _, keeper = started(conv, repo, run, "tree-keeper")
    wrote = keeper_writes(keeper, repo, run, WITH_POINT, "The user confirmed the goal.")
    printed = json.loads(wrote.output)
    assert wrote.exit_code == 0 and printed["doing"] == []
    assert {"goal", HINTS, TYPED} <= set(printed["changed"])
    committed = git(run.worktree, "show", f"HEAD:{run.folder}/design-tree.json")
    assert json.loads(committed) == WITH_POINT
    assert git(run.worktree, "log", "-1", "--format=%B").strip() == "The user confirmed the goal."


@pytest.mark.supports("S1", "tree.py", "Design tree")
def test_write_refuses_a_deliverable_before_one_it_takes_from_and_leaves_the_tree(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the tree-keeper started, and the walkthrough's plan written
    When it writes the plan again with the typed marker before the hints it takes from
    Then tree.py exits 1 naming both paths, and the run's design tree holds the plan as before"""
    _, keeper = started(conv, repo, run, "tree-keeper")
    keeper_writes(keeper, repo, run, WITH_POINT, "The user confirmed the goal.")
    backwards = dict(WITH_POINT, deliverables=WITH_POINT["deliverables"][::-1])
    refused = keeper_writes(keeper, repo, run, backwards, "Typed first.")
    assert refused.exit_code == 1 and HINTS in refused.output and TYPED in refused.output
    held = text_of(os.path.join(run.worktree, run.folder, "design-tree.json"))
    assert json.loads(held) == WITH_POINT


@pytest.mark.supports("S1", "generator", "Cut", "Lack kept", "adapters", "Round")
def test_the_hints_once_due_start_a_generator_with_the_cut_of_its_first_round(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the plan signed off, its point answered, so the hints are marked doing
    When the orchestrator has tree.py cut the generator's cut of the hints, and starts it
    Then its run values name the hints, the kind code, round 1, and a cut whose decisions are the
    hints' alone, with no lack kept"""
    signed_plan(conv, repo, run)
    given, _ = started(conv, repo, run, "generator", HINTS)
    assert (given["deliverable"], given["kind"], given["round"]) == (HINTS, "code", "1")
    held = json.loads(text_of(os.path.join(run.worktree, given["cut"])))
    assert [each["about"] for each in held["decisions"]] == [POINT]
    assert held["lacks"] == []


@pytest.mark.supports("S1", "generator", "tree.py", "Place", "Deliverable")
def test_a_generators_place_commits_its_work_with_the_step_it_stands_at(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running in round 1
    When it writes invoicer/totals.py with hints, and runs
    `tree.py place <run> invoicer/ generator 4`
    Then tree.py exits 0, and the worktree's last commit holds invoicer/totals.py and the round's
    Place of the generator at step 4"""
    signed_plan(conv, repo, run)
    _, generator = started(conv, repo, run, "generator", HINTS)
    generator.write(
        os.path.join(run.worktree, "invoicer", "totals.py"), "def total(lines: list) -> int: ...\n"
    )
    placed = generator.bash(tree(repo, "place", run.folder, HINTS, "generator", "4"))
    committed = git(run.worktree, "show", "--name-only", "--format=", "HEAD").split()
    assert placed.exit_code == 0 and "invoicer/totals.py" in committed
    place = [path for path in committed if path.startswith(f"{run.folder}/rounds/invoicer--/1/")]
    assert place, committed


@pytest.mark.supports("S1", "throwaway.py", "Try record", "generator")
def test_a_try_runs_the_command_in_a_copy_and_keeps_it_in_the_rounds_try_record(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running in round 1
    When it runs `throwaway.py try <run> invoicer/ 1 'python3 -m pytest -q'`
    Then throwaway.py gives the command's exit code and what it printed, and the round's Try record
    holds the command with both"""
    signed_plan(conv, repo, run)
    _, generator = started(conv, repo, run, "generator", HINTS)
    tried = generator.bash(throwaway(repo, "try", run.folder, HINTS, "1", "python3 -m pytest -q"))
    folder = os.path.join(run.worktree, run.folder, "rounds", "invoicer--", "1")
    kept = json.loads(text_of(os.path.join(folder, "try.json")))
    assert kept["tried"][-1]["command"] == "python3 -m pytest -q"
    assert kept["tried"][-1]["exit_code"] == tried.exit_code


@pytest.mark.supports("S1", "generator", "orchestrator")
def test_a_generator_that_asks_ends_with_asks_and_the_next_one_starts_from_the_decision(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running in round 1
    When it gives `asks` on how to type amounts, the point is written open and then decided as
    Decimal, and the orchestrator cuts the generator's cut of the hints again
    Then the guard lets `asks` end the generator, and the new cut holds the Decimal decision in the
    same round"""
    signed_plan(conv, repo, run)
    _, generator = started(conv, repo, run, "generator", HINTS)
    stopped, reached = gives(generator, repo, "generator", "asks", "How should amounts be typed?")
    assert not stopped.blocked and reached
    _, keeper = started(conv, repo, run, "tree-keeper")
    decimal = decided("How amounts are typed", "Decimal", "maker")
    keeper_writes(
        keeper,
        repo,
        run,
        plan(condition("N3", decided(POINT, "each file", "user"), decimal)),
        "As the code computes with Decimal.",
    )
    given, _ = started(conv, repo, run, "generator", HINTS)
    held = json.loads(text_of(os.path.join(run.worktree, given["cut"])))
    assert given["round"] == "1" and decimal in held["decisions"]


@pytest.mark.supports("S1", "generator", "orchestrator")
def test_a_generator_that_lacks_a_tool_ends_with_lacks_and_is_resumed_once_cleared(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running in round 1
    When it gives `lacks` naming mypy, and the orchestrator resumes it once the user installed it
    Then the guard lets `lacks` end it, and lets the resume through"""
    signed_plan(conv, repo, run)
    _, generator = started(conv, repo, run, "generator", HINTS)
    stopped, reached = gives(generator, repo, "generator", "lacks", "mypy isn't installed.")
    resumed = conv.resume(generator, "The main conversation's grounds:\nThe user installed mypy.")
    assert not stopped.blocked and reached and not resumed.blocked


@pytest.mark.supports("S1", "evaluator", "Answers", "Necessary condition", "Round", "adapters")
def test_once_the_generator_is_done_an_evaluator_starts_for_each_group_side_by_side(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator done in round 1, its record and what it made accepted
    When the orchestrator starts an evaluator for each group of the code best practice
    Then each starts beside the others, each with its own group and its own Answers' path in
    round 1"""
    signed_plan(conv, repo, run)
    given, generator = started(conv, repo, run, "generator", HINTS)
    records_all(generator, repo, given, "generator", "code")
    write(
        run.worktree,
        given["made"],
        json.dumps({"decisions": [{"about": POINT, "where": "invoicer/"}], "lacks": []}),
    )
    gives(generator, repo, "generator", "done")
    starts = [started(conv, repo, run, "evaluator", HINTS, group) for group in CODE_GROUPS]
    assert [given["group"] for given, _ in starts] == list(CODE_GROUPS)
    assert len({given["answers"] for given, _ in starts}) == 3
    assert all(given["round"] == "1" and agent.running for given, agent in starts)


@pytest.mark.supports("S1", "orchestrator", "tree-keeper", "Lack kept", "Round", "Decision")
def test_a_lack_the_people_fall_short_by_changes_its_decision_and_reaches_the_next_round(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' round 1 judged, an evaluator naming that callers can't tell a rate from an
    amount
    When the tree-keeper writes the decision it changes and runs `tree.py lack` with the lack, and
    the orchestrator cuts the generator's cut of the hints
    Then the new cut is of round 2, and holds the decision changed and the lack kept"""
    signed_plan(conv, repo, run)
    started(conv, repo, run, "generator", HINTS)
    _, keeper = started(conv, repo, run, "tree-keeper")
    rate = decided("How a rate is typed", "a Decimal named Rate", "maker")
    keeper_writes(
        keeper,
        repo,
        run,
        plan(condition("N3", decided(POINT, "each file", "user"), rate)),
        "A rate reads apart from an amount.",
    )
    lack = "A caller can't tell a rate from an amount."
    kept = keeper.bash(tree(repo, "lack", run.folder, HINTS, "N2", lack))
    given, _ = started(conv, repo, run, "generator", HINTS)
    held = json.loads(text_of(os.path.join(run.worktree, given["cut"])))
    assert kept.exit_code == 0 and given["round"] == "2"
    assert rate in held["decisions"] and held["lacks"] == [{"condition": "N2", "lack": lack}]


@pytest.mark.supports("S1", "guard", "generator")
def test_the_guard_holds_a_generators_end_whose_record_lacks_a_step(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator running in round 1, which recorded no step
    When it gives `done`
    Then the guard holds its end, with what rn's check found missing"""
    signed_plan(conv, repo, run)
    _, generator = started(conv, repo, run, "generator", HINTS)
    stopped, reached = gives(generator, repo, "generator", "done")
    assert stopped.blocked and reached is None
    assert "step 1" in stopped.said


@pytest.mark.supports("S1", "orchestrator", "Deliverable")
def test_a_deliverable_the_orchestrator_sends_back_resumes_its_generator(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator done in round 1, what it made naming no place for one decision
    When the orchestrator resumes it with the ground
    Then the guard lets the resume through, and the generator runs again in round 1"""
    signed_plan(conv, repo, run)
    given, generator = started(conv, repo, run, "generator", HINTS)
    records_all(generator, repo, given, "generator", "code")
    gives(generator, repo, "generator", "done")
    resumed = conv.resume(
        generator, "The main conversation's grounds:\nThe hints of tax.py are missing."
    )
    assert not resumed.blocked and generator.running


@pytest.mark.supports("S1", "evaluator", "Answers")
def test_an_evaluators_end_is_held_until_its_answers_name_each_condition_of_its_group(
    conv: Conversation, repo: Repo, run: Run
):
    """Given an evaluator of the hints' group C1 running, which recorded each step
    When it writes Answers that leave N2 unanswered, and gives `done`
    Then the guard holds its end, naming N2"""
    signed_plan(conv, repo, run)
    given, evaluator = started(conv, repo, run, "evaluator", HINTS, "C1")
    records_all(evaluator, repo, given, "evaluator")
    evaluator.write(
        os.path.join(run.worktree, given["answers"]),
        json.dumps({"met": [{"question": "N1", "lines": ["invoicer/totals.py:1"]}], "not_met": []}),
    )
    stopped, _ = gives(evaluator, repo, "evaluator", "done")
    assert stopped.blocked and "N2" in stopped.said
