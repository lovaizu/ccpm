"""The integration cases of S4, a pause: the user types /rn:dn, the orchestrator stops each role
still running, and tree.py commits each role's work so far with the step it stood at and pushes
it, or says what's missing where it can't push. The test plays the user and the orchestrator, and
the double of gh stands in for GitHub."""

from __future__ import annotations

import json
import os

import pytest
from claude_code import Conversation
from rn_example import (
    ANSWERED,
    HINTS,
    WORDS,
    Repo,
    Run,
    begin,
    conversation,
    git,
    keeper_writes,
    make_repo,
    started,
    tree,
)

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")


def making_hints(conv: Conversation, repo: Repo, run: Run) -> None:
    """The plan written, its point answered, and a generator of the hints started, which writes
    invoicer/tax.py and keeps its Place at step 4."""
    _, keeper = started(conv, repo, run, "tree-keeper")
    keeper_writes(keeper, repo, run, ANSWERED, "The user answered each file.")
    _, generator = started(conv, repo, run, "generator", HINTS)
    generator.write(
        os.path.join(run.worktree, "invoicer", "tax.py"), "def tax(amount: object) -> object: ...\n"
    )
    generator.bash(tree(repo, "place", run.folder, HINTS, "generator", "4"))
    generator.write(
        os.path.join(run.worktree, "invoicer", "totals.py"), "def total() -> None: ...\n"
    )
    conv.task_stop(generator)


@pytest.mark.supports("S4", "tree.py", "Place")
def test_pause_commits_the_work_so_far_with_each_roles_step_and_pushes_it(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator stopped after its Place at step 4, with invoicer/totals.py
    written since
    When the orchestrator runs `tree.py pause`
    Then tree.py exits 0, printing the run's words and the generator at step 4, the remote's branch
    holds invoicer/totals.py, and the worktree has nothing left uncommitted"""
    making_hints(conv, repo, run)
    paused = conv.bash(tree(repo, "pause", run.folder))
    branch = git(run.worktree, "branch", "--show-current").strip()
    assert paused.exit_code == 0 and WORDS in paused.output and "generator" in paused.output
    assert "invoicer/totals.py" in git(repo.remote, "ls-tree", "-r", "--name-only", branch)
    assert git(run.worktree, "status", "--porcelain") == ""


@pytest.mark.supports("S4", "tree.py", "Place")
def test_pause_without_gh_logged_in_commits_and_says_its_not_pushed(tmp_path):
    """Given a run with work not yet committed, and gh logged in nowhere
    When the orchestrator runs `tree.py pause`
    Then tree.py exits 1 with `committed but not pushed` and `gh auth login`, and the worktree has
    nothing left uncommitted"""
    repo = make_repo(os.path.realpath(str(tmp_path)), logged_in=False)
    conv = conversation(repo)
    run = begin(conv, repo)
    making_hints(conv, repo, run)
    paused = conv.bash(tree(repo, "pause", run.folder))
    assert paused.exit_code == 1
    assert "committed but not pushed" in paused.output and "gh auth login" in paused.output
    assert git(run.worktree, "status", "--porcelain") == ""


@pytest.mark.supports("S4", "orchestrator", "generator", "evaluator")
def test_the_orchestrator_stops_each_role_still_running_on_the_pause(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the hints' generator and an evaluator of the typed marker running
    When the user types /rn:dn and the orchestrator stops each by TaskStop
    Then the guard lets each stop through, and neither runs"""
    _, keeper = started(conv, repo, run, "tree-keeper")
    keeper_writes(keeper, repo, run, ANSWERED, "The user answered each file.")
    _, generator = started(conv, repo, run, "generator", HINTS)
    _, evaluator = started(conv, repo, run, "evaluator", HINTS, "C1")
    conv.type("/rn:dn")
    stops = [conv.task_stop(generator), conv.task_stop(evaluator)]
    assert not any(each.blocked for each in stops)
    assert not generator.running and not evaluator.running
    assert json.loads(conv.bash(tree(repo, "runs")).output)["runs"]
