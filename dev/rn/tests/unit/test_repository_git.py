"""The unit cases of repository/git.py, the git commands that tree.py runs by it, through
`make_worktree`, `worktrees`, `commit`, and `push`, on a git repository of the test's own with a
bare repository as its remote."""

from __future__ import annotations

import os
from typing import Any

import pytest
from fault import Missing, Wrong
from repository.git import commit, make_worktree, push, worktrees
from rn_example import git, write
from rn_parts import environ, repository

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")

BRANCH = "rn/20261114-type-hints-for-invoicer"


@pytest.fixture
def repo(tmp_path: Any) -> tuple[str, str, dict[str, str]]:
    root, remote = repository(str(tmp_path))
    return root, remote, environ(str(tmp_path))


@pytest.mark.supports(
    "test_up_with_a_request_makes_the_runs_worktree_on_its_branch_with_its_folder"
)
def test_make_worktree_makes_it_on_a_new_branch_from_head(repo: tuple[str, str, dict[str, str]]):
    """Given the repository with one commit
    When a worktree is made at .claude/worktrees/rn-<run> on the run's branch
    Then git lists it on that branch, at the commit of HEAD"""
    root, _, env = repo
    where = os.path.join(root, ".claude", "worktrees", "rn-20261114-type-hints-for-invoicer")
    make_worktree(root, where, BRANCH, env)
    assert (where, BRANCH) in worktrees(root, env)
    assert git(where, "rev-parse", "HEAD") == git(root, "rev-parse", "HEAD")


@pytest.mark.supports("test_begin_refuses_a_run_that_already_has_its_worktree")
def test_make_worktree_refuses_a_branch_that_exists(repo: tuple[str, str, dict[str, str]]):
    """Given the run's branch already made
    When the worktree is made on it again
    Then it's refused, naming the branch"""
    root, _, env = repo
    git(root, "branch", BRANCH)
    with pytest.raises(Wrong, match=BRANCH):
        make_worktree(root, os.path.join(root, "w"), BRANCH, env)


@pytest.mark.supports("test_runs_with_no_run_left_lists_none")
def test_worktrees_of_a_repository_with_none_made_is_its_own_checkout(
    repo: tuple[str, str, dict[str, str]],
):
    """Given the repository with no worktree made
    When its worktrees are asked for
    Then the one is its own checkout, on main"""
    root, _, env = repo
    assert worktrees(root, env) == ((root, "main"),)


@pytest.mark.supports("test_a_generators_place_commits_its_work_with_the_step_it_stands_at")
def test_commit_commits_each_change_and_says_there_was_one(repo: tuple[str, str, dict[str, str]]):
    """Given invoicer/tax.py written and invoicer/__init__.py changed
    When the worktree is committed with a message
    Then there was a change, the last commit holds both with the message, and nothing is left"""
    root, _, env = repo
    write(root, "invoicer/tax.py", "def tax(amount: object) -> object: ...\n")
    write(root, "invoicer/__init__.py", '"""invoicer, typed."""\n')
    assert commit(root, "generator: step 4 of invoicer/", env) is True
    assert git(root, "log", "-1", "--format=%s").strip() == "generator: step 4 of invoicer/"
    assert git(root, "status", "--porcelain") == ""


@pytest.mark.supports("test_a_generators_place_commits_its_work_with_the_step_it_stands_at")
def test_commit_with_nothing_changed_says_there_was_none(repo: tuple[str, str, dict[str, str]]):
    """Given no change
    When the worktree is committed
    Then there was none, and no commit was made"""
    root, _, env = repo
    head = git(root, "rev-parse", "HEAD")
    assert commit(root, "nothing", env) is False and git(root, "rev-parse", "HEAD") == head


@pytest.mark.supports("test_push_pushes_the_runs_branch_and_opens_its_draft_pull_request_once")
def test_push_sends_the_branch_to_origin(repo: tuple[str, str, dict[str, str]]):
    """Given the run's branch checked out
    When it's pushed
    Then the remote holds the branch at the commit pushed"""
    root, remote, env = repo
    git(root, "checkout", "-q", "-b", BRANCH)
    push(root, BRANCH, env)
    assert git(remote, "rev-parse", BRANCH) == git(root, "rev-parse", "HEAD")


@pytest.mark.supports("test_pause_without_gh_logged_in_commits_and_says_its_not_pushed")
def test_push_without_origin_says_whats_missing(repo: tuple[str, str, dict[str, str]]):
    """Given the repository with its origin removed
    When the branch is pushed
    Then it's Missing, naming origin"""
    root, _, env = repo
    git(root, "remote", "remove", "origin")
    with pytest.raises(Missing, match="origin"):
        push(root, "main", env)
