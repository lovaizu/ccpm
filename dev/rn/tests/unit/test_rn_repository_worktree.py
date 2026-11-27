"""The unit cases of repository/worktree.py: `new`, which makes the work's folder in the worktree
it's given, and each refusal: a folder that isn't a worktree's top, the repository's own checkout,
and work of the name already there; `works` with `left`, the work in each worktree whose branch or
uncommitted changes hold its folder, newest first, the work merged into the default branch left out,
the work ended left out, the work with no steering yet kept, none in a folder that isn't a
repository, and a steering that isn't JSON; and `removed`, the work cancelled here and on GitHub,
the work never pushed, one whose pull request is closed already, what it couldn't ask or remove on
GitHub and why, the repository's own checkout refused, and a worktree git can't remove."""

from __future__ import annotations

import os
from typing import Any

import pytest
import rn_files
from fault import CantRun, Missing, Wrong
from gh import gh_double
from host import run
from place import WorkPlace
from repo_files import git, write_files
from repository.worktree import Gone, left, new, removed, works

NAME = "20261126-invoice-from-statement"
OTHER = "20261127-invoice-rules"
PR = "https://github.com/lovaizu/accounting/pull/1"


@pytest.fixture
def repo(tmp_path: Any) -> str:
    """The user's repository, with origin holding its default branch."""
    made = rn_files.repository(str(tmp_path / "accounting"))
    rn_files.with_origin(made, str(tmp_path / "origin.git"))
    return made


def worktree(repo: str, branch: str = "invoices") -> str:
    """A worktree of the repository beside it, on a new branch from main."""
    return rn_files.worktree_of(repo, os.path.join(os.path.dirname(repo), branch), branch)


def test_the_work_is_made_in_the_worktree_it_is_given(repo: str) -> None:
    """Given the worktree of the user's repository.
    When the work is made in it.
    Then its folder lies there empty, and the worktree's branch stays as it was."""
    made = new(WorkPlace(worktree(repo), NAME), run)
    assert os.listdir(made.folder) == []
    assert git(made.worktree, "branch", "--show-current") == "invoices\n"


def test_a_folder_that_is_not_a_worktrees_top_is_refused(repo: str) -> None:
    """Given a folder inside a worktree.
    When the work is made in it.
    Then Missing is raised, saying to give the work's worktree."""
    inner = os.path.join(worktree(repo), "docs")
    os.makedirs(inner)
    with pytest.raises(Missing, match="isn't the top of a git worktree"):
        new(WorkPlace(inner, NAME), run)


def test_the_repositorys_own_checkout_is_refused(repo: str) -> None:
    """Given the user's repository itself.
    When the work is made in it.
    Then Wrong is raised, saying to give a worktree, and no folder is made."""
    with pytest.raises(Wrong, match="the repository's own checkout"):
        new(WorkPlace(repo, NAME), run)
    assert not os.path.exists(os.path.join(repo, ".rn"))


def test_work_of_a_name_already_taken_is_refused(repo: str) -> None:
    """Given the work made in a worktree.
    When it's made again there.
    Then Wrong is raised, saying to pick it up."""
    made = new(WorkPlace(worktree(repo), NAME), run)
    with pytest.raises(Wrong, match="pick it up with /rn:up"):
        new(made, run)


def committed(work: WorkPlace, steering: Any, when: str) -> None:
    rn_files.committed_steering(work.worktree, work.name, steering, when)


def test_the_work_of_each_worktree_is_found_newest_first(repo: str) -> None:
    """Given a piece of work committed in one worktree, a later piece committed in another, and a
    piece in a third with no steering yet.
    When each piece of work, and each with something left to do, is asked.
    Then the later comes first, each once, and the one with no steering yet is kept."""
    first = new(WorkPlace(worktree(repo, "first"), NAME), run)
    committed(first, rn_files.steering(), "2026-11-26T09:00:00")
    later = new(WorkPlace(worktree(repo, "later"), OTHER), run)
    committed(later, rn_files.steering(), "2026-11-27T09:00:00")
    fresh = new(WorkPlace(worktree(repo, "fresh"), "20261128-print"), run)
    write_files(fresh.folder, {"notes.md": "for the accountants\n"})
    found = works(repo, run)
    assert (found.index(later) < found.index(first), sorted(found, key=str)) == (
        True,
        sorted([first, later, fresh], key=str),
    )
    assert set(left(repo, run)) == {later, first, fresh}


def test_the_work_ended_or_merged_is_left_out(repo: str) -> None:
    """Given the work whose steering has ended, and other work merged into the default branch.
    When the work with something left to do is asked.
    Then neither is found."""
    ended = new(WorkPlace(worktree(repo, "ended"), NAME), run)
    done = rn_files.steering([rn_files.step("done")])
    done["state"]["inspected"] = True
    committed(ended, done, "2026-11-26T09:00:00")
    merged = new(WorkPlace(worktree(repo, "merged"), OTHER), run)
    committed(merged, rn_files.steering(), "2026-11-27T09:00:00")
    git(repo, "merge", "-q", "merged")
    git(repo, "push", "-q", "origin", "main")
    assert left(repo, run) == []


def test_the_work_is_found_where_origin_names_no_head(repo: str) -> None:
    """Given the work committed in a worktree, and origin's HEAD unset, as a clone made otherwise
    than by `git clone` leaves it.
    When the work with something left to do is asked.
    Then it's found, by origin's main."""
    made = new(WorkPlace(worktree(repo), NAME), run)
    committed(made, rn_files.steering(), "2026-11-26T09:00:00")
    git(repo, "remote", "set-head", "origin", "-d")
    assert left(repo, run) == [made]


def test_the_work_is_found_where_git_holds_no_default_branch(repo: str) -> None:
    """Given the work committed in a worktree, and no ref of origin's default branch.
    When the work with something left to do is asked.
    Then it's found, by the branch's own tree."""
    made = new(WorkPlace(worktree(repo), NAME), run)
    committed(made, rn_files.steering(), "2026-11-26T09:00:00")
    git(repo, "remote", "set-head", "origin", "-d")
    git(repo, "update-ref", "-d", "refs/remotes/origin/main")
    assert left(repo, run) == [made]


def test_a_folder_that_is_not_a_repository_holds_no_work_of_rn(tmp_path: Any) -> None:
    """Given a folder that lies in no git repository.
    When the work is asked.
    Then there are none."""
    assert works(str(tmp_path), run) == []


def test_a_steering_that_is_not_json_is_refused(repo: str) -> None:
    """Given the work whose steering isn't JSON.
    When the work with something left to do is asked.
    Then Wrong is raised, naming its path."""
    made = new(WorkPlace(worktree(repo), NAME), run)
    write_files(made.folder, {"steering.json": "{"})
    with pytest.raises(Wrong, match="steering.json: isn't JSON"):
        left(repo, run)


def pushed(repo: str) -> WorkPlace:
    """The work made in a worktree, with its branch pushed to origin."""
    made = new(WorkPlace(worktree(repo), NAME), run)
    git(made.worktree, "push", "-q", "origin", "invoices")
    return made


def test_the_cancelled_work_is_removed_here_and_on_github(
    repo: str, host: Any, gh_state: str
) -> None:
    """Given the work pushed with its pull request open, and a change in it not committed.
    When it's removed.
    Then the pull request is closed and origin's branch deleted, each named, the worktree, the
    local branch, and origin's ref are gone, and the user's branch stays main."""
    made = pushed(repo)
    gh_double.opened(gh_state, PR)
    write_files(made.worktree, {"draft.md": "draft\n"})
    assert removed(made, host) == Gone([PR, "origin/invoices"], [])
    assert not os.path.exists(made.worktree)
    assert git(repo, "branch", "--list", "invoices") == ""
    assert git(repo, "branch", "-r", "--list", "origin/invoices") == ""
    assert gh_double.state(gh_state)["pull_request"] is None
    assert git(repo, "branch", "--show-current") == "main\n"


def test_the_work_in_the_users_own_worktree_leaves_the_worktree_and_its_branch(
    repo: str, host: Any
) -> None:
    """Given the work made in the user's own worktree, pushed, and a change of theirs not
    committed.
    When it's removed.
    Then the work's folder alone is gone, committed and pushed as `rn: cancelled <name>`, the
    worktree, its branch, and the user's change stay, and what's kept is named."""
    made = new(WorkPlace(worktree(repo), NAME), run, users=True)
    rn_files.committed_steering(made.worktree, NAME, rn_files.steering())
    git(made.worktree, "push", "-q", "origin", "invoices")
    write_files(made.worktree, {"draft.md": "draft\n"})
    kept = "the branch invoices, its commits, and its pull request, as the worktree is the user's"
    assert removed(made, host) == Gone([], [kept])
    assert not os.path.exists(made.folder)
    assert os.path.isfile(os.path.join(made.worktree, "draft.md"))
    assert git(made.worktree, "log", "-1", "--format=%s") == f"rn: cancelled {NAME}\n"
    assert git(repo, "rev-parse", "origin/invoices") == git(made.worktree, "rev-parse", "HEAD")


def test_the_cancel_in_the_users_own_worktree_says_what_git_couldnt_push(
    repo: str, host: Any
) -> None:
    """Given the work made in the user's own worktree, and a repository with no origin.
    When it's removed.
    Then the work's folder is gone and committed, and the push it couldn't make is named."""
    made = new(WorkPlace(worktree(repo), NAME), run, users=True)
    rn_files.committed_steering(made.worktree, NAME, rn_files.steering())
    git(repo, "remote", "remove", "origin")
    gone = removed(made, host)
    assert gone.kept[1].startswith("the cancel's commit on GitHub, as git can't push it: ")
    assert not os.path.exists(made.folder)


def test_the_work_never_pushed_is_removed_here_and_its_stale_ref_with_it(
    repo: str, host: Any
) -> None:
    """Given the work with no pull request, which origin doesn't hold, but whose ref of origin's
    branch is left here.
    When it's removed.
    Then nothing is named on GitHub, and the worktree, the branch, and the ref are gone."""
    made = new(WorkPlace(worktree(repo), NAME), run)
    git(repo, "update-ref", "refs/remotes/origin/invoices", "invoices")
    assert removed(made, host) == Gone([], [])
    assert not os.path.exists(made.worktree)
    assert git(repo, "for-each-ref", "refs/remotes/origin/invoices") == ""


def test_a_pull_request_closed_already_is_left_as_it_is(
    repo: str, host: Any, gh_state: str
) -> None:
    """Given a pushed work whose branch has only an earlier pull request, closed.
    When it's removed.
    Then gh closes nothing, and origin's branch alone is named."""
    made = pushed(repo)
    gh_double.earlier(gh_state, PR, "CLOSED")
    assert removed(made, host) == Gone(["origin/invoices"], [])
    assert not any(each[1:3] == ["pr", "close"] for each in gh_double.state(gh_state)["asked"])


def test_what_github_couldnt_be_asked_of_is_kept_with_why(
    repo: str, host: Any, gh_state: str
) -> None:
    """Given the work, with gh unable to reach GitHub and origin gone.
    When it's removed.
    Then it's removed here, and the pull request and the branch on GitHub are kept, each with
    what gh or git said."""
    made = new(WorkPlace(worktree(repo), NAME), run)
    gh_double.unreached(gh_state)
    git(repo, "remote", "set-url", "origin", os.path.join(repo, "no-such-origin"))
    gone = removed(made, host)
    assert gone.removed == []
    assert gone.kept[0].startswith("the pull request of invoices on GitHub, as gh can't ask")
    assert gone.kept[1].startswith("the branch invoices on GitHub, as git can't ask origin: ")
    assert not os.path.exists(made.worktree)


def test_what_github_refused_to_remove_is_kept_with_why(
    repo: str, tmp_path: Any, host: Any, gh_state: str
) -> None:
    """Given a pushed work with its pull request open, gh losing GitHub once it read it, and origin
    refusing each push.
    When it's removed.
    Then the pull request and the branch on GitHub are kept, each with what gh or git said."""
    made = pushed(repo)
    gh_double.opened(gh_state, PR)
    gh_double.closes_unreached(gh_state)
    hook = tmp_path / "origin.git" / "hooks" / "pre-receive"
    hook.write_text("#!/bin/sh\necho no deletes here >&2\nexit 1\n")
    hook.chmod(0o755)
    gone = removed(made, host)
    assert gone.removed == []
    assert gone.kept[0].startswith(f"the pull request {PR} on GitHub, as gh can't close it: ")
    assert gone.kept[1].startswith("the branch invoices on GitHub, as git can't delete it: ")
    assert "no deletes here" in gone.kept[1]


def test_the_repositorys_own_checkout_is_never_removed(repo: str, host: Any) -> None:
    """Given the work whose folder lies in the user's repository itself.
    When it's removed.
    Then Wrong is raised, and the checkout stays."""
    held = WorkPlace(repo, NAME)
    os.makedirs(held.folder)
    with pytest.raises(Wrong, match="which rn never removes"):
        removed(held, host)
    assert os.path.isdir(held.folder)


def test_a_worktree_git_cant_remove_cant_run_and_keeps_the_branch(repo: str, host: Any) -> None:
    """Given the work whose worktree is locked.
    When it's removed.
    Then CantRun is raised with what git said, and the worktree and the branch stay."""
    made = new(WorkPlace(worktree(repo), NAME), run)
    git(repo, "worktree", "lock", made.worktree)
    with pytest.raises(CantRun, match="locked"):
        removed(made, host)
    assert os.path.isdir(made.worktree)
    assert git(repo, "branch", "--list", "invoices") != ""
