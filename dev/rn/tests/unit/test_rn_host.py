"""The unit cases of host.py's `run`, the one way rn's code reaches git and gh:
git giving 0 with its stdout, git with variables of its environment given, gh on the PATH giving
another code with its stdout and stderr whole, and each refusal: a program of another name, and a
program not found."""

from __future__ import annotations

import os
from typing import Any

import pytest
import rn_files
from fault import CantRun, Wrong
from host import Ran, checked, run


def test_git_runs_in_the_folder_given_and_gives_its_output(tmp_path: Any):
    """Given a git repository
    When run is given `git rev-parse --show-toplevel` in it
    Then it gives 0, the repository's top and a newline as stdout, and no stderr"""
    repo = rn_files.repository(str(tmp_path / "accounting"))
    assert run(["git", "rev-parse", "--show-toplevel"], repo) == Ran(0, repo + "\n", "")


def test_git_runs_with_the_variables_given_beside_rns_own(tmp_path: Any):
    """Given a git repository
    When run is given `git var GIT_AUTHOR_IDENT` in it, with GIT_AUTHOR_NAME set to `Ada`
    Then it gives 0, git naming Ada as the author, and rn's own environment keeps its value"""
    repo = rn_files.repository(str(tmp_path / "accounting"))
    before = os.environ.get("GIT_AUTHOR_NAME")
    ran = run(["git", "var", "GIT_AUTHOR_IDENT"], repo, {"GIT_AUTHOR_NAME": "Ada"})
    assert ran.code == 0
    assert ran.out.startswith("Ada <")
    assert os.environ.get("GIT_AUTHOR_NAME") == before


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


def test_a_program_other_than_git_or_gh_is_refused(tmp_path: Any):
    """Given git2, a program named other than git or gh
    When run is given it
    Then Wrong is raised, naming it"""
    with pytest.raises(Wrong, match="'git2'"):
        run(["git2", "--version"], str(tmp_path))


def test_a_program_not_found_cant_run(tmp_path: Any, monkeypatch: pytest.MonkeyPatch):
    """Given a PATH that holds no gh
    When run is given `gh auth status`
    Then CantRun is raised, naming gh"""
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setenv("PATH", str(empty))
    with pytest.raises(CantRun, match="gh"):
        run(["gh", "auth", "status"], str(tmp_path))


def test_checked_gives_what_a_command_gave_where_it_gives_0(tmp_path: Any):
    """Given a git repository
    When checked runs `git rev-parse --show-toplevel` in it, as one that must give 0
    Then it gives what git gave"""
    repo = rn_files.repository(str(tmp_path / "accounting"))
    ran = checked(run, ["git", "rev-parse", "--show-toplevel"], repo, CantRun, "find the top")
    assert ran == Ran(0, repo + "\n", "")


def test_checked_raises_the_fault_given_where_a_command_fails(tmp_path: Any):
    """Given a folder that's no git repository
    When checked runs `git rev-parse --show-toplevel` in it, with Wrong as its fault
    Then Wrong is raised, saying what the command did and what git printed"""
    with pytest.raises(Wrong, match="find the top: fatal: not a git repository"):
        checked(run, ["git", "rev-parse", "--show-toplevel"], str(tmp_path), Wrong, "find the top")
