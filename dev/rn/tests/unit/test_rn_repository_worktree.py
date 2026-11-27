"""The unit cases of repository/worktree.py: `new`, which makes a run's folder in the worktree it's
given, and each refusal: a folder that isn't a worktree's top, the repository's own checkout, and
a run of the name already there; `runs` with `left`, the runs in each worktree whose branch or
uncommitted changes hold their folder, newest first, a run merged into the default branch left
out, a run ended left out, a run with no steering yet kept, no run in a folder that isn't a
repository, and a steering that isn't JSON; and `removed`, a run cancelled here and on GitHub, one
never pushed, one whose pull request is closed already, what it couldn't ask or remove on GitHub
and why, the repository's own checkout refused, and a worktree git can't remove."""

from __future__ import annotations

import os
from typing import Any

import pytest
import rn_files
from fault import CantRun, Missing, Wrong
from gh import gh_double
from host import run
from place import RunPlace
from repo_files import git, write_files
from repository.worktree import Gone, left, new, removed, runs

NAME = "20261126-invoice-from-statement"
OTHER = "20261127-invoice-rules"
PR = "https://github.com/lovaizu/accounting/pull/1"


@pytest.fixture
def repo(tmp_path: Any) -> str:
    """The user's repository, with origin holding its default branch."""
    made = rn_files.repository(str(tmp_path / "accounting"))
    rn_files.with_origin(made, str(tmp_path / "origin.git"))
    return made


def worktree(repo: str, branch: str = "work") -> str:
    """A worktree of the repository beside it, on a new branch from main."""
    return rn_files.worktree_of(repo, os.path.join(os.path.dirname(repo), branch), branch)


def test_a_run_is_made_in_the_worktree_it_is_given(repo: str) -> None:
    """Given a worktree of the user's repository.
    When a run is made in it.
    Then its folder lies there empty, and the worktree's branch stays as it was."""
    made = new(RunPlace(worktree(repo), NAME), run)
    assert os.listdir(made.folder) == []
    assert git(made.worktree, "branch", "--show-current") == "work\n"


def test_a_folder_that_is_not_a_worktrees_top_is_refused(repo: str) -> None:
    """Given a folder inside a worktree.
    When a run is made in it.
    Then Missing is raised, saying to give the run's worktree."""
    inner = os.path.join(worktree(repo), "docs")
    os.makedirs(inner)
    with pytest.raises(Missing, match="isn't the top of a git worktree"):
        new(RunPlace(inner, NAME), run)


def test_the_repositorys_own_checkout_is_refused(repo: str) -> None:
    """Given the user's repository itself.
    When a run is made in it.
    Then Wrong is raised, saying to give a worktree, and no folder is made."""
    with pytest.raises(Wrong, match="the repository's own checkout"):
        new(RunPlace(repo, NAME), run)
    assert not os.path.exists(os.path.join(repo, ".rn"))


def test_a_run_of_the_same_name_is_refused(repo: str) -> None:
    """Given a run made in a worktree.
    When it's made again there.
    Then Wrong is raised, saying to pick it up."""
    made = new(RunPlace(worktree(repo), NAME), run)
    with pytest.raises(Wrong, match="pick it up with /rn:up"):
        new(made, run)


def committed(run_: RunPlace, steering: Any, when: str) -> None:
    rn_files.committed_steering(run_.worktree, run_.name, steering, when)


def test_the_runs_of_each_worktree_are_found_newest_first(repo: str) -> None:
    """Given a run committed in one worktree, a later one committed in another, and one in a third
    with no steering yet.
    When the runs and those with work left are asked.
    Then the later comes first, each once, and the one with no steering yet is kept."""
    first = new(RunPlace(worktree(repo, "first"), NAME), run)
    committed(first, rn_files.steering(), "2026-11-26T09:00:00")
    later = new(RunPlace(worktree(repo, "later"), OTHER), run)
    committed(later, rn_files.steering(), "2026-11-27T09:00:00")
    fresh = new(RunPlace(worktree(repo, "fresh"), "20261128-print"), run)
    write_files(fresh.folder, {"pruner.json": "{}\n"})
    found = runs(repo, run)
    assert (found.index(later) < found.index(first), sorted(found, key=str)) == (
        True,
        sorted([first, later, fresh], key=str),
    )
    assert set(left(repo, run)) == {later, first, fresh}


def test_a_run_ended_or_merged_is_left_out(repo: str) -> None:
    """Given a run whose steering has ended, and a run merged into the default branch.
    When the runs with work left are asked.
    Then neither is found."""
    ended = new(RunPlace(worktree(repo, "ended"), NAME), run)
    done = rn_files.steering([rn_files.step("done")])
    done["state"]["inspected"] = True
    committed(ended, done, "2026-11-26T09:00:00")
    merged = new(RunPlace(worktree(repo, "merged"), OTHER), run)
    committed(merged, rn_files.steering(), "2026-11-27T09:00:00")
    git(repo, "merge", "-q", "merged")
    git(repo, "push", "-q", "origin", "main")
    assert left(repo, run) == []


def test_a_folder_that_is_not_a_repository_holds_no_run(tmp_path: Any) -> None:
    """Given a folder that lies in no git repository.
    When the runs are asked.
    Then there are none."""
    assert runs(str(tmp_path), run) == []


def test_a_steering_that_is_not_json_is_refused(repo: str) -> None:
    """Given a run whose steering isn't JSON.
    When the runs with work left are asked.
    Then Wrong is raised, naming its path."""
    made = new(RunPlace(worktree(repo), NAME), run)
    write_files(made.folder, {"steering.json": "{"})
    with pytest.raises(Wrong, match="steering.json: isn't JSON"):
        left(repo, run)


def pushed(repo: str) -> RunPlace:
    """A run made in a worktree, with its branch pushed to origin."""
    made = new(RunPlace(worktree(repo), NAME), run)
    git(made.worktree, "push", "-q", "origin", "work")
    return made


def test_a_cancelled_run_is_removed_here_and_on_github(repo: str, host: Any, gh_state: str) -> None:
    """Given a run pushed with its pull request open, and a change in it not committed.
    When it's removed.
    Then the pull request is closed and origin's branch deleted, each named, the worktree, the
    local branch, and origin's ref are gone, and the user's branch stays main."""
    made = pushed(repo)
    gh_double.opened(gh_state, PR)
    write_files(made.worktree, {"draft.md": "draft\n"})
    assert removed(made, host) == Gone([PR, "origin/work"], [])
    assert not os.path.exists(made.worktree)
    assert git(repo, "branch", "--list", "work") == ""
    assert git(repo, "branch", "-r", "--list", "origin/work") == ""
    assert gh_double.state(gh_state)["pull_request"] is None
    assert git(repo, "branch", "--show-current") == "main\n"


def test_a_run_never_pushed_is_removed_here_and_its_stale_ref_with_it(repo: str, host: Any) -> None:
    """Given a run with no pull request, which origin doesn't hold, but whose ref of origin's
    branch is left here.
    When it's removed.
    Then nothing is named on GitHub, and the worktree, the branch, and the ref are gone."""
    made = new(RunPlace(worktree(repo), NAME), run)
    git(repo, "update-ref", "refs/remotes/origin/work", "work")
    assert removed(made, host) == Gone([], [])
    assert not os.path.exists(made.worktree)
    assert git(repo, "for-each-ref", "refs/remotes/origin/work") == ""


def test_a_pull_request_closed_already_is_left_as_it_is(
    repo: str, host: Any, gh_state: str
) -> None:
    """Given a pushed run whose branch has only an earlier pull request, closed.
    When it's removed.
    Then gh closes nothing, and origin's branch alone is named."""
    made = pushed(repo)
    gh_double.earlier(gh_state, PR, "CLOSED")
    assert removed(made, host) == Gone(["origin/work"], [])
    assert not any(each[1:3] == ["pr", "close"] for each in gh_double.state(gh_state)["asked"])


def test_what_github_couldnt_be_asked_of_is_kept_with_why(
    repo: str, host: Any, gh_state: str
) -> None:
    """Given a run, with gh unable to reach GitHub and origin gone.
    When it's removed.
    Then it's removed here, and the pull request and the branch on GitHub are kept, each with
    what gh or git said."""
    made = new(RunPlace(worktree(repo), NAME), run)
    gh_double.unreached(gh_state)
    git(repo, "remote", "set-url", "origin", os.path.join(repo, "no-such-origin"))
    gone = removed(made, host)
    assert gone.removed == []
    assert gone.kept[0].startswith("the pull request of work on GitHub, as gh can't ask")
    assert gone.kept[1].startswith("the branch work on GitHub, as git can't ask origin: ")
    assert not os.path.exists(made.worktree)


def test_what_github_refused_to_remove_is_kept_with_why(
    repo: str, tmp_path: Any, host: Any, gh_state: str
) -> None:
    """Given a pushed run with its pull request open, gh losing GitHub once it read it, and origin
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
    assert gone.kept[1].startswith("the branch work on GitHub, as git can't delete it: ")
    assert "no deletes here" in gone.kept[1]


def test_the_repositorys_own_checkout_is_never_removed(repo: str, host: Any) -> None:
    """Given a run whose folder lies in the user's repository itself.
    When it's removed.
    Then Wrong is raised, and the checkout stays."""
    held = RunPlace(repo, NAME)
    os.makedirs(held.folder)
    with pytest.raises(Wrong, match="which rn never removes"):
        removed(held, host)
    assert os.path.isdir(held.folder)


def test_a_worktree_git_cant_remove_cant_run_and_keeps_the_branch(repo: str, host: Any) -> None:
    """Given a run whose worktree is locked.
    When it's removed.
    Then CantRun is raised with what git said, and the worktree and the branch stay."""
    made = new(RunPlace(worktree(repo), NAME), run)
    git(repo, "worktree", "lock", made.worktree)
    with pytest.raises(CantRun, match="locked"):
        removed(made, host)
    assert os.path.isdir(made.worktree)
    assert git(repo, "branch", "--list", "work") != ""
