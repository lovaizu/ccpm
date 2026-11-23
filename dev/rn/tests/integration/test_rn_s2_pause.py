"""The integration cases of S2, a pause, a cancel, and a pick-up: each path through its sequence,
the pause while a generator makes, while an evaluator tries, and while a point waits; the cancel,
done or failing where the worktree can't be removed; and the pick-up from the runs' commits, of a
run whose worktree and local branch are gone, and of none. Each runs rn's scripts as the
orchestrator and each role run them, with the double of gh, and a double of each prompt's work."""

from __future__ import annotations

import os

import pytest
import rn_files
from gh import gh_double
from repo_files import git
from rn_bench import (
    Bench,
    cut_move,
    evaluator_cut,
    held,
    pointed,
    reviewed,
    signed_plan,
    wrote,
)
from rn_files import COMMAND


def paused(b: Bench) -> str:
    """The orchestrator, with each role stopped, commits and pushes the run by repository.py
    pause; gives the hash that pause printed."""
    return b.ran("repository", "pause", b.run).strip()


def picked_up(b: Bench) -> None:
    """In a new conversation, the orchestrator finds the run by repository.py find, which prints
    the run's folder, and commits its review."""
    assert b.ran("repository", "find").split() == [b.run]
    reviewed(b, ground="Picked up.")


def mid_command(b: Bench) -> None:
    """A run whose command's generator writes the command in its Round content-1."""
    signed_plan(b)
    wrote(b, {COMMAND: "print('invoice')\n"})


@pytest.mark.supports("S2", "Design tree")
def test_a_pause_pushes_the_runs_work_so_far(b: Bench):
    """Given a run whose command's generator writes the command, not committed
    When the user pauses the run, and the orchestrator runs repository.py pause
    Then pause prints the head of the remote's branch rn-<name>, which holds the run's design tree,
    the command's Cut, and the command, and the work's branch has nothing left uncommitted"""
    mid_command(b)
    printed = paused(b)
    branch = f"rn-{b.name()}"
    assert printed == git(b.origin, "rev-parse", branch).strip()
    files = b.branch_files(branch)
    folder = os.path.relpath(b.folder, b.worktree)
    cut = os.path.relpath(rn_files.round_of(b.folder, COMMAND, "content", 1), b.worktree)
    assert f"{folder}/design-tree.json" in files
    assert f"{cut}/generator-cut.json" in files
    assert COMMAND in files
    assert git(b.worktree, "status", "--porcelain").strip() == ""


@pytest.mark.supports("S2", "Round")
def test_a_pause_while_the_evaluator_tries_pushes_its_cut(b: Bench):
    """Given a run whose command's evaluator has its Cut
    When the user pauses the run
    Then the remote's branch holds the evaluator's Cut"""
    evaluator_cut(b)
    paused(b)
    cut = os.path.relpath(rn_files.round_of(b.folder, COMMAND, "content", 1), b.worktree)
    assert f"{cut}/evaluator-cut.json" in b.branch_files(f"rn-{b.name()}")


@pytest.mark.supports("S2")
def test_a_pause_leaves_the_users_own_worktree_and_branch_as_they_were(b: Bench):
    """Given a run whose command's generator writes the command, and a file the user is changing
    on main
    When the user pauses the run
    Then main's head, the user's checked-out branch, and their change are as they were"""
    mid_command(b)
    head = git(b.repo, "rev-parse", "main").strip()
    with open(b.at("NOTES.md"), "w", encoding="utf-8") as f:
        f.write("The user's own notes.\n")
    paused(b)
    assert git(b.repo, "rev-parse", "main").strip() == head
    assert git(b.repo, "branch", "--show-current").strip() == "main"
    assert git(b.repo, "status", "--porcelain").strip() == "?? NOTES.md"


@pytest.mark.supports("S2", "Round", "Cut")
def test_a_pick_up_starts_the_stopped_generator_again_in_its_round_with_a_fresh_cut(b: Bench):
    """Given a run paused while its command's generator made Round content-1
    When the user types /rn:up in a new conversation, and the orchestrator finds the run and
    writes the generator's Cut
    Then the Cut lies in Round content-1 again"""
    mid_command(b)
    paused(b)
    picked_up(b)
    cut_path = b.ran(*cut_move(b, "generator", COMMAND)).strip()
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert os.path.join(b.repo, cut_path) == os.path.join(first, "generator-cut.json")


@pytest.mark.supports("S2", "Round", "Cut")
def test_a_pick_up_starts_the_stopped_evaluator_again_in_its_round(b: Bench):
    """Given a run paused while its command's evaluator tried Round content-1
    When the user picks it up in a new conversation, and the orchestrator writes the evaluator's
    Cut
    Then the Cut lies in Round content-1"""
    evaluator_cut(b)
    paused(b)
    picked_up(b)
    cut_path = b.ran(*cut_move(b, "evaluator", COMMAND)).strip()
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert os.path.join(b.repo, cut_path) == os.path.join(first, "evaluator-cut.json")


@pytest.mark.supports("S2", "Design tree")
def test_a_pick_up_with_a_point_waiting_keeps_it_open_and_starts_no_role(b: Bench):
    """Given a run paused while the generator's point waits on the user, kept as an open
    decision of the command's N1
    When the user picks it up in a new conversation
    Then the design tree still holds the point open, and tree.py cut of the generator gives 1, as
    the command waits on the user's answer"""
    pointed(b, signed_plan(b), "Should a line's quantity default to 1?")
    point = rn_files.decision("a line's quantity", None)
    reviewed(b, held(b, COMMAND, [], {"N1": [point]}), "The generator's point.")
    paused(b)
    picked_up(b)
    assert point in b.tree()["deliverables"][1]["necessary_conditions"][0]["decisions"]
    refused = b.script(*cut_move(b, "generator", COMMAND))
    assert refused.code == 1
    assert "the user's answer" in refused.err


@pytest.mark.supports("S2", "scripts", "Design tree")
def test_a_pick_up_in_a_repository_whose_worktree_is_gone_makes_it_again(b: Bench):
    """Given a run paused while its command's generator made it, whose worktree and local branch
    the user then removed, so that only origin's branch holds the run
    When the user types /rn:up in a new conversation, the orchestrator runs repository.py find,
    and writes the generator's Cut
    Then find prints the run's folder, its worktree lies there again on rn-<name> at origin's
    head, holding the design tree that the pause pushed, and the Cut lies in Round content-1"""
    mid_command(b)
    paused(b)
    pushed = b.tree()
    git(b.repo, "worktree", "remove", "--force", b.worktree)
    git(b.repo, "branch", "-D", f"rn-{b.name()}")
    assert b.ran("repository", "find").split() == [b.run]
    assert (
        git(b.worktree, "rev-parse", "HEAD").strip()
        == git(b.origin, "rev-parse", f"rn-{b.name()}").strip()
    )
    assert b.tree() == pushed
    reviewed(b, ground="Picked up.")
    cut_path = b.ran(*cut_move(b, "generator", COMMAND)).strip()
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert os.path.join(b.repo, cut_path) == os.path.join(first, "generator-cut.json")


@pytest.mark.supports("S2")
def test_a_pick_up_with_no_run_finds_none_and_makes_no_worktree(b: Bench):
    """Given invoicer's repository with no run of rn
    When the user types /rn:up, and the orchestrator runs repository.py find
    Then it prints nothing, for the orchestrator to ask which run to pick up, and the repository
    has no worktree of rn"""
    assert b.ran("repository", "find") == ""
    assert not os.path.exists(b.at(".claude/worktrees"))


@pytest.mark.supports("S2", "Design tree")
def test_a_new_request_in_a_paused_runs_words_leaves_the_run_as_it_was(b: Bench):
    """Given a run paused while its command's generator made it
    When the user asks again in the same words, and the orchestrator runs repository.py new
    Then new gives 1, refusing the run's name as taken, and the worktree's design tree is as the
    pause left it"""
    mid_command(b)
    paused(b)
    before = b.tree()
    refused = b.script("repository", "new", rn_files.NAMED, rn_files.GOAL, *rn_files.LANGUAGES)
    assert refused.code == 1
    assert b.name() in refused.err
    assert b.tree() == before


@pytest.mark.supports("S2", "scripts")
def test_a_cancel_removes_the_worktree_its_branch_and_its_pull_request(b: Bench):
    """Given a run whose plan's pull request is open and whose command's generator makes it
    When the user confirms the cancel, and the orchestrator, with the generator stopped, runs
    repository.py cancel
    Then cancel prints the pull request and origin's branch, which it removed on GitHub; the run's
    worktree, its local branch, and origin's branch are gone, and the pull request is closed"""
    mid_command(b)
    pr = b.tree()["context"]["pr"]
    printed = b.ran("repository", "cancel", b.run)
    assert printed.splitlines() == [pr, f"origin/rn-{b.name()}"]
    assert not os.path.exists(b.worktree)
    assert git(b.repo, "branch", "--list", f"rn-{b.name()}").strip() == ""
    assert f"rn-{b.name()}" not in git(b.origin, "branch", "--list")
    assert gh_double.state(b.gh)["pull_request"] is None


@pytest.mark.supports("S2", "scripts")
def test_a_cancel_whose_worktree_cant_be_removed_gives_2_and_keeps_the_run(b: Bench):
    """Given a run whose command's generator makes it, and whose worktree is locked
    When the user confirms the cancel, and the orchestrator runs repository.py cancel
    Then it gives 2, and the worktree and its branch stay"""
    mid_command(b)
    git(b.repo, "worktree", "lock", b.worktree)
    refused = b.script("repository", "cancel", b.run)
    assert refused.code == 2
    assert os.path.isdir(b.worktree)
    assert git(b.repo, "branch", "--list", f"rn-{b.name()}").strip() != ""
