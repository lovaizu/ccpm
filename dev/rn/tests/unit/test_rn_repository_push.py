"""The unit cases of push.py: `stop`, which commits each change and pushes with its upstream set,
and each refusal: no origin, a push refused for want of a permission, and a remote that isn't
there; and `kept`, which commits and pushes, then, once a need is picked, asks gh's login, its
first time opening the pull request as a draft titled by the picked need, its body the outcome and
the issues, or the outcome alone, an open pull request used as it is, its own opened beside an
earlier one closed, no pull request before a need is picked, and each refusal after the push: gh
with no login, gh that may not open the pull request, and gh that can't tell whether one is
open."""

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
URL = "http://github.com/owner/repo/pull/1"
STEERING = rn_files.steering()


def made(tmp_path: Any, origin: bool = True) -> WorkPlace:
    """The user's repository with origin, unless not, and a work made in it, its steering
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


def asked(gh_state: str, *words: str) -> list[list[str]]:
    """Each gh command that the double was asked whose words after `gh` begin with those given."""
    return [
        each
        for each in gh_double.state(gh_state)["asked"]
        if each[1 : 1 + len(words)] == list(words)
    ]


def flag(argv: list[str], name: str) -> str:
    """The value that a command names after the flag."""
    return argv[argv.index(name) + 1]


# stop


def test_a_stop_commits_each_change_and_pushes_the_branch_with_its_upstream(
    tmp_path: Any, host: Any
) -> None:
    """Given a work whose command is new, not committed.
    When stop is given the work.
    Then it gives the hash that origin's branch now holds, a commit `rn: stopped <name>`, whose
    upstream is origin's, with nothing left uncommitted."""
    work = with_command(made(tmp_path))
    given = stop(work, None, host)
    assert given == head(str(tmp_path / "origin.git"), BRANCH) == head(work.worktree)
    assert subject(work.worktree) == f"rn: stopped {NAME}"
    upstream = git(work.worktree, "rev-parse", "--abbrev-ref", f"{BRANCH}@{{upstream}}").strip()
    assert (upstream, git(work.worktree, "status", "--porcelain")) == (f"origin/{BRANCH}", "")


def test_a_stop_with_no_origin_is_missing_one(tmp_path: Any, host: Any) -> None:
    """Given a work whose repository has no remote.
    When stop is given the work.
    Then Missing is raised."""
    with pytest.raises(Missing, match="no remote origin"):
        stop(made(tmp_path, origin=False), None, host)


def test_a_stop_whose_push_is_refused_for_want_of_a_permission_is_missing_one(
    tmp_path: Any, host: Any
) -> None:
    """Given a work whose remote's files may not be written.
    When stop is given the work.
    Then Missing is raised, with what git said of the permission."""
    work = with_command(made(tmp_path))
    origin = str(tmp_path / "origin.git")
    for folder, _, files in os.walk(origin):
        for each in [folder, *(os.path.join(folder, f) for f in files)]:
            os.chmod(each, os.stat(each).st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
    try:
        with pytest.raises(Missing, match=r"(?s)a permission: .*\[remote rejected\]"):
            stop(work, None, host)
    finally:
        for folder, _, _ in os.walk(origin):
            os.chmod(folder, os.stat(folder).st_mode | stat.S_IWUSR)


def test_a_stop_to_a_remote_that_isnt_there_cant_run(tmp_path: Any, host: Any) -> None:
    """Given a work whose remote origin names a folder that doesn't exist.
    When stop is given the work.
    Then CantRun is raised, with what git said."""
    work = made(tmp_path, origin=False)
    git(work.worktree, "remote", "add", "origin", str(tmp_path / "gone.git"))
    with pytest.raises(CantRun, match="push the work: .*does not appear to be a git repo"):
        stop(work, None, host)


# kept

MESSAGE = "rn: invoice/__main__.py: done"


def test_a_first_kept_opens_the_pull_request_as_a_draft_titled_by_the_picked_need(
    tmp_path: Any, host: Any, gh_state: str
) -> None:
    """Given a work whose command is made, with a need picked and no pull request.
    When kept is given the work and a message.
    Then the command is committed with the message and pushed, gh's login is asked, and a draft
    pull request is opened of the branch titled by the picked need, its body the outcome and
    `Closes #38`."""
    work = with_command(made(tmp_path))
    pushed = kept(work, STEERING, MESSAGE, host)
    assert pushed == head(str(tmp_path / "origin.git"), BRANCH) == head(work.worktree)
    assert subject(work.worktree) == MESSAGE
    assert gh_double.state(gh_state)["asked"][0][:3] == ["gh", "auth", "status"]
    [create] = asked(gh_state, "pr", "create")
    assert ("--draft" in create, flag(create, "--head"), flag(create, "--title")) == (
        True,
        BRANCH,
        rn_files.PRINT,
    )
    assert flag(create, "--body") == f"{rn_files.OUTCOME}\n\nCloses #38"


def test_a_kept_names_each_issue_it_closes_then_each_it_refers_to_or_none(
    tmp_path: Any, host: Any, gh_state: str
) -> None:
    """Given a work that closes #38 and #40 and refers to #12, and another that names none.
    When each is kept first.
    Then the first body names `Closes #38`, `Closes #40`, then `Refs #12`, and the second is the
    outcome alone."""
    work = with_command(made(tmp_path))
    issues = rn_files.steering()
    issues["state"]["issues"] = {"closes": [38, 40], "refs": [12]}
    kept(work, issues, MESSAGE, host)
    none = rn_files.steering()
    none["state"]["issues"] = {"closes": [], "refs": []}
    gh_double.keep(gh_state, {**gh_double.state(gh_state), "pull_request": None})
    kept(work, none, MESSAGE, host)
    bodies = [flag(each, "--body") for each in asked(gh_state, "pr", "create")]
    assert bodies == [f"{rn_files.OUTCOME}\n\nCloses #38\nCloses #40\nRefs #12", rn_files.OUTCOME]


def test_a_kept_whose_pull_request_is_open_opens_none(
    tmp_path: Any, host: Any, gh_state: str
) -> None:
    """Given a work whose branch has its pull request open.
    When kept is given the work.
    Then it opens no pull request."""
    work = with_command(made(tmp_path))
    gh_double.opened(gh_state, URL)
    kept(work, STEERING, MESSAGE, host)
    assert asked(gh_state, "pr", "create") == []


def test_a_kept_beside_an_earlier_pull_request_not_open_opens_its_own(
    tmp_path: Any, host: Any, gh_state: str
) -> None:
    """Given a work whose branch's name had a pull request that's closed.
    When kept is given the work.
    Then it opens a pull request of its own."""
    work = with_command(made(tmp_path))
    gh_double.earlier(gh_state, "http://github.com/owner/repo/pull/0", "CLOSED")
    kept(work, STEERING, MESSAGE, host)
    assert len(asked(gh_state, "pr", "create")) == 1


@pytest.mark.parametrize(
    "steering", [None, rn_files.steering(target=None)], ids=["no-steering", "no-need-picked"]
)
def test_a_kept_before_a_need_is_picked_pushes_and_asks_gh_nothing(
    tmp_path: Any, host: Any, gh_state: str, steering: Any
) -> None:
    """Given a work with no steering yet, or none whose need is picked.
    When kept is given it.
    Then the change is committed and pushed, and gh is asked nothing."""
    work = with_command(made(tmp_path))
    kept(work, steering, MESSAGE, host)
    assert head(str(tmp_path / "origin.git"), BRANCH) == head(work.worktree)
    assert gh_double.state(gh_state)["asked"] == []


def test_a_kept_with_gh_logged_out_pushes_then_is_missing_its_login(
    tmp_path: Any, host: Any, gh_state: str
) -> None:
    """Given gh with no login.
    When kept is given the work.
    Then the change is pushed, and Missing is raised."""
    work = with_command(made(tmp_path))
    gh_double.logged_out(gh_state)
    with pytest.raises(Missing, match="no login"):
        kept(work, STEERING, MESSAGE, host)
    assert head(str(tmp_path / "origin.git"), BRANCH) == head(work.worktree)


def test_a_kept_that_gh_may_not_open_is_missing_the_right(tmp_path: Any, host: Any) -> None:
    """Given gh that refuses to open the pull request.
    When kept is given the work.
    Then Missing is raised, with what gh said."""
    work = with_command(made(tmp_path))

    def refusing(argv: Sequence[str], cwd: str, env: Mapping[str, str] | None = None) -> Ran:
        return (
            Ran(1, "", "must be a collaborator\n")
            if argv[1:3] == ["pr", "create"]
            else host(argv, cwd, env)
        )

    with pytest.raises(Missing, match="may not open the pull request: must be a collaborator"):
        kept(work, STEERING, MESSAGE, refusing)


def test_a_kept_whose_gh_cant_reach_github_opens_no_second_pull_request(
    tmp_path: Any, host: Any, gh_state: str
) -> None:
    """Given a work whose branch has its pull request open, and gh that can't reach GitHub to view
    it.
    When kept is given the work.
    Then CantRun is raised with what gh said, and no pull request is opened."""
    work = with_command(made(tmp_path))
    gh_double.opened(gh_state, URL)
    gh_double.unreached(gh_state)
    with pytest.raises(CantRun, match="can't tell whether the branch has a pull request"):
        kept(work, STEERING, MESSAGE, host)
    assert asked(gh_state, "pr", "create") == []
