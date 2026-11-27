"""The unit cases of push.py: `stop`, which commits each change and pushes with its upstream set,
and each refusal: no origin, a push refused for want of a permission, and a remote that isn't
there; and `kept`, which commits the paths given, or each change, and pushes, a push that git
refuses kept for the next, and no origin missing one."""

from __future__ import annotations

import os
import stat
from collections.abc import Mapping, Sequence
from typing import Any

import pytest
import rn_files
from fault import CantRun, Missing
from gh import gh_double
from host import Ran
from place import WorkPlace
from push import kept, stop
from repo_files import git, write_files
from repository.worktree import new

BRANCH = "invoices"
NAME = "20261126-invoice-from-statement"
STEERING = rn_files.steering()


def made(tmp_path: Any, origin: bool = True) -> WorkPlace:
    """The user's repository with origin, unless not, and the work made in it, its steering
    committed."""
    repo = rn_files.repository(str(tmp_path / "accounting"))
    if origin:
        rn_files.with_origin(repo, str(tmp_path / "origin.git"))
    else:
        git(repo, "update-ref", "refs/remotes/origin/HEAD", "HEAD")
        git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
        git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    worktree = rn_files.worktree_of(repo, str(tmp_path / "invoices"), BRANCH)
    work = new(WorkPlace(worktree, NAME), gh_double.host(str(tmp_path / "unused")))
    rn_files.committed_steering(work.worktree, NAME, STEERING)
    return work


def with_command(work: WorkPlace) -> WorkPlace:
    """The work, with the command written in its worktree, as its generator leaves it."""
    write_files(work.worktree, {rn_files.COMMAND: "print('invoice')\n"})
    return work


def head(folder: str, ref: str = "HEAD") -> str:
    return git(folder, "rev-parse", ref).strip()


def subject(folder: str) -> str:
    return git(folder, "log", "-1", "--format=%s").strip()


# stop


def test_a_stop_commits_each_change_and_pushes_the_branch_with_its_upstream(
    tmp_path: Any, host: Any
) -> None:
    """Given the work whose command is new, not committed.
    When stop is given the work.
    Then it gives the hash that origin's branch now holds, a commit `rn: stopped <name>`, whose
    upstream is origin's, with nothing left uncommitted."""
    work = with_command(made(tmp_path))
    given = stop(work, host)
    assert given == head(str(tmp_path / "origin.git"), BRANCH) == head(work.worktree)
    assert subject(work.worktree) == f"rn: stopped {NAME}"
    upstream = git(work.worktree, "rev-parse", "--abbrev-ref", f"{BRANCH}@{{upstream}}").strip()
    assert (upstream, git(work.worktree, "status", "--porcelain")) == (f"origin/{BRANCH}", "")


def test_a_stop_with_no_origin_is_missing_one(tmp_path: Any, host: Any) -> None:
    """Given the work whose repository has no remote.
    When stop is given the work.
    Then Missing is raised."""
    with pytest.raises(Missing, match="no remote origin"):
        stop(made(tmp_path, origin=False), host)


def test_a_stop_whose_push_is_refused_for_want_of_a_permission_is_missing_one(
    tmp_path: Any, host: Any
) -> None:
    """Given the work whose remote's files may not be written.
    When stop is given the work.
    Then Missing is raised, with what git said of the permission."""
    work = with_command(made(tmp_path))
    origin = str(tmp_path / "origin.git")
    for folder, _, files in os.walk(origin):
        for each in [folder, *(os.path.join(folder, f) for f in files)]:
            os.chmod(each, os.stat(each).st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
    try:
        with pytest.raises(Missing, match=r"(?s)a permission: .*\[remote rejected\]"):
            stop(work, host)
    finally:
        for folder, _, _ in os.walk(origin):
            os.chmod(folder, os.stat(folder).st_mode | stat.S_IWUSR)


def test_a_stop_to_a_remote_that_isnt_there_cant_run(tmp_path: Any, host: Any) -> None:
    """Given the work whose remote origin names a folder that doesn't exist.
    When stop is given the work.
    Then CantRun is raised, with what git said."""
    work = made(tmp_path, origin=False)
    git(work.worktree, "remote", "add", "origin", str(tmp_path / "gone.git"))
    with pytest.raises(CantRun, match="push the work: .*does not appear to be a git repo"):
        stop(work, host)


# kept

MESSAGE = "rn: invoice/__main__.py: done"


def test_a_kept_commits_each_change_and_pushes_it(tmp_path: Any, host: Any) -> None:
    """Given the work whose command is new, not committed.
    When kept is given the work, with no paths.
    Then it gives "", the command committed with the message, and origin's branch holds it."""
    work = with_command(made(tmp_path))
    assert kept(work, MESSAGE, None, host) == ""
    assert (subject(work.worktree), git(work.worktree, "status", "--porcelain")) == (MESSAGE, "")
    assert head(str(tmp_path / "origin.git"), BRANCH) == head(work.worktree)


def test_a_kept_with_paths_commits_those_alone(tmp_path: Any, host: Any) -> None:
    """Given the work whose steering changed, and whose command a role is still writing.
    When kept is given the work, with the steering's path.
    Then the steering alone is committed, and the command is left as it is."""
    work = with_command(made(tmp_path))
    rn_files.write_json(work.steering, rn_files.steering([]))
    assert kept(work, MESSAGE, [work.steering], host) == ""
    assert git(work.worktree, "status", "--porcelain") == "?? invoice/\n"


def test_a_kept_whose_push_git_refuses_keeps_the_commit_for_the_next(
    tmp_path: Any, host: Any
) -> None:
    """Given the work whose origin names a folder that doesn't exist.
    When kept is given the work.
    Then it gives what git said, and the commit is kept."""
    work = with_command(made(tmp_path, origin=False))
    git(work.worktree, "remote", "add", "origin", str(tmp_path / "gone.git"))
    said = kept(work, MESSAGE, None, host)
    assert ("does not appear to be a git repo" in said, subject(work.worktree)) == (True, MESSAGE)


def test_a_kept_with_no_origin_is_missing_one(tmp_path: Any, host: Any) -> None:
    """Given the work whose repository has no remote.
    When kept is given the work.
    Then Missing is raised, the commit kept."""
    work = with_command(made(tmp_path, origin=False))
    with pytest.raises(Missing, match="no remote origin"):
        kept(work, MESSAGE, None, host)
    assert subject(work.worktree) == MESSAGE


def test_a_kept_whose_commit_git_refuses_cant_run(tmp_path: Any, host: Any) -> None:
    """Given the work whose command is new, and git that refuses each commit.
    When kept is given the work.
    Then CantRun is raised, with what git said."""
    work = with_command(made(tmp_path))

    def refusing(argv: Sequence[str], cwd: str, env: Mapping[str, str] | None = None) -> Ran:
        return Ran(1, "", "hook refused\n") if argv[1] == "commit" else host(argv, cwd, env)

    with pytest.raises(CantRun, match="git commit fails: hook refused"):
        kept(work, MESSAGE, None, refusing)
