"""The unit cases of repository/worktree.py: `new`, which makes a run's worktree on its branch from
origin's default branch with its folder empty and the worktrees kept out of the user's untracked
files, and each refusal: a folder that isn't a repository's top, a run of the name already there,
no default branch on origin, and git refusing the worktree; and `found` with `left`, the runs with
work left, newest first, each once, a run all done or with no steering left out, a worktree made
again from its local branch or from origin's, the local branches alone where git can't fetch, no
run in a folder that isn't a repository, and a steering that isn't JSON."""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from typing import Any

import pytest
import rn_files
from fault import CantRun, Missing, Wrong
from host import Ran, run
from place import RunPlace
from repo_files import git
from repository.worktree import found, left, new

NAME = "20261126-invoice-from-statement"
OTHER = "20261127-invoice-rules"


@pytest.fixture
def repo(tmp_path: Any) -> str:
    """The user's repository, with origin holding its default branch."""
    made = rn_files.repository(str(tmp_path / "accounting"))
    rn_files.with_origin(made, str(tmp_path / "origin.git"))
    return made


def test_a_run_is_made_on_its_branch_from_origins_default_branch(repo: str) -> None:
    """Given the user's repository with origin's HEAD naming main.
    When a run is made.
    Then its worktree holds main's files on the branch rn-<name>, its folder lies
    there empty, the user's branch stays main, and info/exclude keeps the worktrees out once."""
    made = new(RunPlace(repo, NAME), run)
    new(RunPlace(repo, OTHER), run)
    assert git(made.worktree, "branch", "--show-current") == f"{made.branch}\n"
    assert os.listdir(made.folder) == []
    assert os.path.isfile(os.path.join(made.worktree, "README.md"))
    assert git(repo, "branch", "--show-current") == "main\n"
    assert git(repo, "status", "--porcelain") == ""
    with open(os.path.join(repo, ".git", "info", "exclude"), encoding="utf-8") as f:
        assert f.read().splitlines().count("/.claude/worktrees/") == 1


def test_a_folder_that_is_not_a_repositorys_top_is_refused(repo: str) -> None:
    """Given a folder inside the user's repository, below its top.
    When a run is made there.
    Then Missing is raised, asking for /rn:on at the top."""
    inside = os.path.join(repo, "docs")
    os.makedirs(inside)
    with pytest.raises(Missing, match="isn't the top of a git repository"):
        new(RunPlace(inside, NAME), run)


def test_a_run_of_the_same_name_is_refused(repo: str) -> None:
    """Given a run of the name already made.
    When it's made again.
    Then Wrong is raised, pointing to /rn:up."""
    new(RunPlace(repo, NAME), run)
    with pytest.raises(Wrong, match="/rn:up"):
        new(RunPlace(repo, NAME), run)


def test_a_repository_with_no_default_branch_on_origin_is_refused(tmp_path: Any) -> None:
    """Given a repository with no remote.
    When a run is made.
    Then Missing is raised, saying how to name the default branch."""
    bare = rn_files.repository(str(tmp_path / "accounting"))
    with pytest.raises(Missing, match="set-head origin --auto"):
        new(RunPlace(bare, NAME), run)


def test_git_refusing_the_worktree_cant_run(repo: str) -> None:
    """Given git that refuses to add a worktree.
    When a run is made.
    Then CantRun is raised with what git said."""

    def refusing(argv: Sequence[str], cwd: str, env: Mapping[str, str] | None = None) -> Ran:
        return (
            Ran(128, "", "fatal: no room\n")
            if argv[1:3] == ["worktree", "add"]
            else run(argv, cwd, env)
        )

    with pytest.raises(CantRun, match="fatal: no room"):
        new(RunPlace(repo, NAME), refusing)


def made_with(repo: str, name: str, steps: list[Any] | None, when: str) -> RunPlace:
    """A run made, with its steering of the steps committed at the time, or none where None."""
    made = new(RunPlace(repo, name), run)
    if steps is not None:
        rn_files.committed_steering(made.worktree, name, rn_files.steering(steps), when)
    return made


def test_the_runs_with_work_left_are_found_newest_first(repo: str) -> None:
    """Given a run with a step open, a newer one with no step yet, one with each step done, and one
    with no steering.
    When the runs are found.
    Then the two with work left are given, the newer first, and nothing is unchecked."""
    older = made_with(repo, NAME, [rn_files.step()], "2026-11-26T09:00:00")
    newer = made_with(repo, OTHER, [], "2026-11-27T09:00:00")
    made_with(repo, "20261125-done", [rn_files.step("done")], "2026-11-28T09:00:00")
    made_with(repo, "20261124-bare", None, "")
    git(older.worktree, "push", "-q", "origin", older.branch)
    assert found(repo, run) == ([newer, older], None)


def test_a_worktree_gone_is_made_again_from_its_branch(repo: str) -> None:
    """Given a run with work left whose worktree was removed, and another on origin alone.
    When the runs are found.
    Then each worktree lies there again, on its branch."""
    here = made_with(repo, NAME, [rn_files.step()], "2026-11-26T09:00:00")
    there = made_with(repo, OTHER, [rn_files.step()], "2026-11-27T09:00:00")
    git(there.worktree, "push", "-q", "origin", there.branch)
    for each in (here, there):
        git(repo, "worktree", "remove", "--force", each.worktree)
    git(repo, "branch", "-D", there.branch)
    assert found(repo, run).runs == [there, here]
    assert git(there.worktree, "branch", "--show-current") == f"{there.branch}\n"
    assert os.path.isfile(here.steering)


def test_the_local_branches_alone_count_where_git_cant_fetch(repo: str) -> None:
    """Given a run with work left, and origin gone.
    When the runs are found.
    Then the run is given, with what couldn't be checked on GitHub."""
    made = made_with(repo, NAME, [rn_files.step()], "2026-11-26T09:00:00")
    git(repo, "remote", "set-url", "origin", os.path.join(repo, "no-such-origin"))
    runs, unchecked = found(repo, run)
    assert runs == [made]
    assert unchecked is not None and unchecked.startswith(
        "the runs on GitHub, as git can't ask origin: "
    )


def test_a_folder_that_is_not_a_repository_holds_no_run(tmp_path: Any) -> None:
    """Given a folder that isn't a git repository.
    When the runs with work left are asked.
    Then none is given."""
    assert left(str(tmp_path), run) == []


def test_a_steering_that_is_not_json_is_refused(repo: str) -> None:
    """Given a run whose committed steering isn't JSON.
    When the runs with work left are asked.
    Then Wrong is raised, naming the branch and the path."""
    made = new(RunPlace(repo, NAME), run)
    with open(made.steering, "w", encoding="utf-8") as f:
        f.write("{")
    git(made.worktree, "add", "-A")
    git(made.worktree, "commit", "-q", "-m", "broken")
    with pytest.raises(Wrong, match=f"rn-{NAME}:.rn/{NAME}/steering.json: isn't JSON"):
        left(repo, run)
