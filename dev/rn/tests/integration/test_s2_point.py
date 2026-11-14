"""The integration cases of S2, a point settled: a point that's the user's goes into the design tree
as a decision still open before the user sees it, the work that rests on no open point goes on
meanwhile, and the decision, once settled by the user or by the purpose and the best practices, is
written with its ground and marks each deliverable whose turn has come doing. The test plays the
user, the orchestrator, and the tree-keeper."""

from __future__ import annotations

import json

import pytest
from claude_code import Conversation
from rn_example import (
    ANSWER,
    ANSWERED,
    HINTS,
    POINT,
    WITH_POINT,
    Repo,
    Run,
    condition,
    decided,
    git,
    keeper_writes,
    plan,
    started,
    tree,
)

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")


def signed(conv: Conversation, repo: Repo, run: Run, design: dict) -> None:
    """The design tree written, and the plan signed off by the user's /rn:ty."""
    _, keeper = started(conv, repo, run, "tree-keeper")
    keeper_writes(keeper, repo, run, design, "The plan.")
    path = f"{repo.temp}/plan.json"
    conv.write(None, path, json.dumps({"of": "plan", "can_do": "", "decisions": [], "words": ""}))
    conv.bash(tree(repo, "sign-off", run.folder, path))
    conv.type("/rn:ty")


@pytest.mark.supports("S2", "tree-keeper", "Point", "Decision", "tree.py")
def test_a_users_point_written_open_keeps_the_deliverable_it_lies_under_from_doing(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the plan signed off, with the point on each file open under the hints
    When the tree-keeper writes the design tree again on the sign-off
    Then tree.py marks no deliverable doing, as the hints rest on the open point and the typed
    marker on the hints"""
    signed(conv, repo, run, WITH_POINT)
    _, keeper = started(conv, repo, run, "tree-keeper")
    wrote = keeper_writes(keeper, repo, run, WITH_POINT, "The user signed the plan off.")
    assert wrote.exit_code == 0 and json.loads(wrote.output)["doing"] == []


@pytest.mark.supports("S2", "tree-keeper", "Decision", "tree.py", "user")
def test_the_users_answer_written_with_its_ground_marks_the_hints_doing_and_checks_the_path_up(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the plan signed off, with the point on each file open
    When the tree-keeper writes the user's answer `each file`, by the user, with its ground
    Then tree.py prints the decision as changed, the goal and the hints among the nodes it
    touches, and the hints doing, and commits the tree with the ground as its message"""
    signed(conv, repo, run, WITH_POINT)
    _, keeper = started(conv, repo, run, "tree-keeper")
    wrote = keeper_writes(keeper, repo, run, ANSWERED, "The user answered each file.")
    printed = json.loads(wrote.output)
    assert f"{HINTS} N3: {POINT}" in printed["changed"]
    assert {"goal", HINTS} <= set(printed["touched"]) and printed["doing"] == [HINTS]
    committed = json.loads(git(run.worktree, "show", f"HEAD:{run.folder}/design-tree.json"))
    assert committed["deliverables"][0]["status"] == "doing"
    assert git(run.worktree, "log", "-1", "--format=%B").strip() == "The user answered each file."


@pytest.mark.supports("S2", "orchestrator", "Decision")
def test_a_point_the_best_practice_settles_is_written_by_reasoning_with_no_open_decision_before_it(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the plan signed off, its point answered
    When the tree-keeper writes a decision on how the hints are checked, settled by reasoning
    Then tree.py takes it at once, with no open decision in the tree before it"""
    signed(conv, repo, run, ANSWERED)
    _, keeper = started(conv, repo, run, "tree-keeper")
    checked = decided("How the hints are checked", "mypy --strict over invoicer/", "reasoning")
    wrote = keeper_writes(
        keeper,
        repo,
        run,
        plan(condition("N3", decided(POINT, ANSWER, "user")), condition("N7", checked)),
        "By the code best practice.",
    )
    assert wrote.exit_code == 0
    assert f"{HINTS} N7: How the hints are checked" in json.loads(wrote.output)["changed"]


@pytest.mark.supports("S2", "tree.py", "Decision")
def test_write_refuses_a_decision_whose_by_is_none_the_schema_takes(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the plan written
    When the tree-keeper writes the answer with `by` as `orchestrator`
    Then tree.py exits 1 naming `by` and each value the schema takes, so that the orchestrator
    sends the change back"""
    signed(conv, repo, run, WITH_POINT)
    _, keeper = started(conv, repo, run, "tree-keeper")
    wrong = plan(condition("N3", decided(POINT, ANSWER, "orchestrator")))
    refused = keeper_writes(keeper, repo, run, wrong, "The user answered each file.")
    assert refused.exit_code == 1 and "by" in refused.output and "reasoning" in refused.output


@pytest.mark.supports("S2", "orchestrator", "tree-keeper")
def test_a_change_that_falls_short_is_sent_back_to_the_tree_keeper_by_its_resume(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the tree-keeper ended with the answer written
    When the orchestrator resumes it with the ground on which the change falls short
    Then the guard lets the resume through, and the tree-keeper runs again"""
    _, keeper = started(conv, repo, run, "tree-keeper")
    keeper_writes(keeper, repo, run, ANSWERED, "The user answered each file.")
    keeper.end("Wrote the answer.")
    resumed = conv.resume(
        keeper,
        "The main conversation's grounds:\nThe typed marker still says only callers' functions.",
    )
    assert not resumed.blocked and keeper.running


@pytest.mark.supports("S2", "tree.py", "Point")
def test_runs_names_the_point_that_waits_for_the_user(conv: Conversation, repo: Repo, run: Run):
    """Given the plan written with the point on each file open
    When the orchestrator runs `tree.py runs`
    Then the run's line names the point as what waits"""
    _, keeper = started(conv, repo, run, "tree-keeper")
    keeper_writes(keeper, repo, run, WITH_POINT, "The plan.")
    listed = json.loads(conv.bash(tree(repo, "runs")).output)["runs"]
    assert [each["waiting"] for each in listed] == [POINT]
