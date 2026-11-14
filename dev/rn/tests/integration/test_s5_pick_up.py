"""The integration cases of S5, picking up: the user types /rn:up alone in a new conversation,
tree.py lists the runs left, the orchestrator enters the run's worktree, and each role that stood
in a step starts again at that step, while the guard picks the run up from the results that rn
kept. The test plays the user, the orchestrator, and each role."""

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
    conversation,
    gives,
    keeper_writes,
    records_all,
    started,
    text_of,
    tree,
)

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")


def paused_at_step_4(conv: Conversation, repo: Repo, run: Run) -> None:
    """The plan written, its point answered, the hints' generator at step 4, and the run paused."""
    _, keeper = started(conv, repo, run, "tree-keeper")
    keeper_writes(keeper, repo, run, ANSWERED, "The user answered each file.")
    _, generator = started(conv, repo, run, "generator", HINTS)
    generator.bash(tree(repo, "place", run.folder, HINTS, "generator", "4"))
    conv.task_stop(generator)
    conv.bash(tree(repo, "pause", run.folder))


@pytest.mark.supports("S5", "tree.py")
def test_runs_with_no_run_left_lists_none(conv: Conversation, repo: Repo):
    """Given the repository of invoicer with no run of rn
    When the user types /rn:up alone and the orchestrator runs `tree.py runs`
    Then tree.py exits 0 with no run"""
    conv.type("/rn:up")
    listed = conv.bash(tree(repo, "runs"))
    assert listed.exit_code == 0 and json.loads(listed.output) == {"runs": []}


@pytest.mark.supports("S5", "tree.py", "Place")
def test_runs_lists_the_run_paused_with_what_it_was_making_and_where(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the run paused while the hints' generator stood at step 4
    When the user types /rn:up alone in a new conversation and the orchestrator runs `tree.py runs`
    Then tree.py lists the one run, with its words, its worktree, the hints as made, and the
    generator at step 4"""
    paused_at_step_4(conv, repo, run)
    fresh = conversation(repo)
    fresh.type("/rn:up")
    (left,) = json.loads(fresh.bash(tree(repo, "runs")).output)["runs"]
    assert (left["words"], left["worktree"]) == (WORDS, run.worktree)
    assert left["making"] == ["Type hints in each file of invoicer, checked by mypy --strict"]
    assert left["places"] == [{"role": "generator", "step": 4}]


@pytest.mark.supports("S5", "tree.py", "Point")
def test_runs_lists_each_of_two_runs_left_for_the_user_to_pick(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the walkthrough's run and a second run begun on README for invoicer
    When the orchestrator runs `tree.py runs` in a new conversation
    Then tree.py lists both, in the order of their names"""
    conv.exit_worktree("keep")
    conv.bash(tree(repo, "begin", "README for invoicer"))
    listed = json.loads(conversation(repo).bash(tree(repo, "runs")).output)["runs"]
    assert [each["words"] for each in listed] == ["README for invoicer", WORDS]


@pytest.mark.supports("S5", "generator", "Cut", "Place", "orchestrator")
def test_the_picked_up_generator_starts_at_the_step_it_stood_at(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the run paused while the hints' generator stood at step 4
    When the orchestrator of a new conversation enters the run's worktree and cuts the generator's
    cut of the hints
    Then the cut is of the same round, and holds the generator's Place at step 4"""
    paused_at_step_4(conv, repo, run)
    fresh = conversation(repo)
    fresh.type("/rn:up")
    fresh.enter_worktree(path=run.worktree)
    given, _ = started(fresh, repo, run, "generator", HINTS)
    held = json.loads(text_of(os.path.join(run.worktree, given["cut"])))
    assert given["round"] == "1" and held["place"]["step"] == 4


@pytest.mark.supports("S5", "adapters", "guard", "tree-keeper")
def test_the_guard_of_a_new_conversation_picks_the_run_up_from_the_results_kept(
    conv: Conversation, repo: Repo, run: Run
):
    """Given the tree-keeper's `done` accepted by rn's check and kept in its record, and the run
    paused
    When a new conversation enters the run's worktree and the user types /rn:up alone
    Then the guard adds no start of the tree-keeper from the run's first move, as it picked up
    the result kept"""
    given, keeper = started(conv, repo, run, "tree-keeper")
    keeper_writes(keeper, repo, run, ANSWERED, "The user answered each file.")
    records_all(keeper, repo, given, "tree-keeper", "design-tree")
    gives(keeper, repo, "tree-keeper", "done")
    conv.bash(tree(repo, "pause", run.folder))
    fresh = conversation(repo)
    fresh.enter_worktree(path=run.worktree)
    typed = fresh.type("/rn:up")
    assert "rn:tree-keeper" not in typed.said
    assert json.loads(text_of(os.path.join(run.worktree, given["record"])))["result"] == "done"
