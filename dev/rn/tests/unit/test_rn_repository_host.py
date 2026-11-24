"""The unit cases of repository/host.py's `run`, the one way rn's code reaches git, gh, and herdr:
one for each class of what it takes, git, gh, herdr, and a program of another name, a near match
among them, and variables of its environment given and none; and of what it gives, a command that
gives 0 and one that gives another code, each with its stdout and stderr whole; and the refusal of
a program not found."""

from __future__ import annotations

import os
from typing import Any

import pytest
import rn_files
from fault import CantRun, Wrong
from repository.host import Ran, run


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_open"
)
def test_git_runs_in_the_folder_given_and_gives_its_output(tmp_path: Any):
    """Given a git repository
    When run is given `git rev-parse --show-toplevel` in it
    Then it gives 0, the repository's top and a newline as stdout, and no stderr"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    assert run(["git", "rev-parse", "--show-toplevel"], repo) == Ran(0, repo + "\n", "")


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_open"
)
def test_git_that_fails_gives_its_code_and_stderr_whole(tmp_path: Any):
    """Given a folder that isn't a git repository
    When run is given `git status` in it
    Then it gives git's code, 128, no stdout, and git's stderr saying it's not a git repository"""
    folder = str(tmp_path)
    ran = run(["git", "status"], folder)
    assert (ran.code, ran.out) == (128, "")
    assert "not a git repository" in ran.err


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_open"
)
def test_git_changes_what_its_command_changes(tmp_path: Any):
    """Given an empty folder
    When run is given `git init -q` in it
    Then it gives 0 with no output, and the folder holds a git repository"""
    folder = str(tmp_path)
    assert run(["git", "init", "-q"], folder) == Ran(0, "", "")
    assert os.path.isdir(os.path.join(folder, ".git"))


@pytest.mark.supports("test_the_generators_checks_judge_its_files_alone_beside_another_staged")
def test_git_runs_with_the_variables_given_beside_rns_own(tmp_path: Any):
    """Given a git repository
    When run is given `git var GIT_AUTHOR_IDENT` in it, with GIT_AUTHOR_NAME set to `Ada`
    Then it gives 0, git naming Ada as the author, and rn's own environment keeps its value"""
    repo = rn_files.repository(str(tmp_path / "invoicer"))
    before = os.environ.get("GIT_AUTHOR_NAME")
    ran = run(["git", "var", "GIT_AUTHOR_IDENT"], repo, {"GIT_AUTHOR_NAME": "Ada"})
    assert ran.code == 0
    assert ran.out.startswith("Ada <")
    assert os.environ.get("GIT_AUTHOR_NAME") == before


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
def test_gh_runs_as_the_program_on_the_path(tmp_path: Any, monkeypatch: pytest.MonkeyPatch):
    """Given a program gh first on the PATH that prints its arguments and gives 3
    When run is given `gh pr view 12`
    Then it gives 3, `pr view 12` and a newline as stdout, and what it said on stderr"""
    bin_folder = tmp_path / "bin"
    bin_folder.mkdir()
    gh = bin_folder / "gh"
    gh.write_text('#!/bin/sh\necho "$@"\necho said >&2\nexit 3\n')
    gh.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_folder}{os.pathsep}{os.environ['PATH']}")
    assert run(["gh", "pr", "view", "12"], str(tmp_path)) == Ran(3, "pr view 12\n", "said\n")


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_open"
)
def test_herdr_runs_as_the_program_on_the_path(tmp_path: Any, monkeypatch: pytest.MonkeyPatch):
    """Given a program herdr first on the PATH that prints its arguments and gives 1
    When run is given `herdr worktree open --no-focus`
    Then it gives 1, `worktree open --no-focus` and a newline as stdout, and what it said on
    stderr"""
    bin_folder = tmp_path / "bin"
    bin_folder.mkdir()
    herdr = bin_folder / "herdr"
    herdr.write_text('#!/bin/sh\necho "$@"\necho said >&2\nexit 1\n')
    herdr.chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_folder}{os.pathsep}{os.environ['PATH']}")
    argv = ["herdr", "worktree", "open", "--no-focus"]
    assert run(argv, str(tmp_path)) == Ran(1, "worktree open --no-focus\n", "said\n")


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_open"
)
@pytest.mark.parametrize("program", ["ls", "gitk", "git2", "ghx", "herdrx", "/usr/bin/git", ""])
def test_a_program_other_than_git_or_gh_is_refused(tmp_path: Any, program: str):
    """Given a program named other than git, gh, or herdr, a near match or git by its path among
    them
    When run is given it
    Then Wrong is raised, and nothing runs"""
    with pytest.raises(Wrong):
        run([program, "--version"], str(tmp_path))


@pytest.mark.supports("test_the_plan_waiting_for_signoff_is_put_up_in_the_runs_pull_request")
def test_a_program_not_found_cant_run(tmp_path: Any, monkeypatch: pytest.MonkeyPatch):
    """Given a PATH that holds no gh
    When run is given `gh auth status`
    Then CantRun is raised, naming gh"""
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setenv("PATH", str(empty))
    with pytest.raises(CantRun, match="gh"):
        run(["gh", "auth", "status"], str(tmp_path))
