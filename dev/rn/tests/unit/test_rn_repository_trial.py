"""The unit cases of repository/trial.py, the folder of the people's starting state in which an
evaluator tries a deliverable: where it lies by its Round, a folder outside the run's Rounds
refused, the work's branch as committed cloned there without rn's folder, one left there made
anew, and git that can't clone."""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from typing import Any

import pytest
import rn_files
from fault import CantRun, Wrong
from host import Ran, run
from place import RunPlace
from repo_files import git, write_files
from repository.trial import folder, starting_state

NAME = "20261126-invoice-from-statement"


@pytest.fixture
def made(tmp_path: Any) -> RunPlace:
    """A run whose worktree holds its steering and the command committed, as rn's hook commits
    each role's changes, and a draft written since, not committed."""
    repo = rn_files.repository(str(tmp_path / "accounting"))
    held = RunPlace(repo, NAME)
    git(repo, "worktree", "add", "-q", "-b", held.branch, held.worktree)
    rn_files.committed_steering(held.worktree, NAME, rn_files.steering())
    write_files(held.worktree, {rn_files.COMMAND: "print('invoice')\n"})
    git(held.worktree, "add", "-A")
    git(held.worktree, "commit", "-q", "-m", "the command")
    write_files(held.worktree, {"draft.md": "not yet\n"})
    return held


def round_of(run_: RunPlace) -> str:
    return os.path.join(run_.rounds, "invoice%2F__main__.py", "content-1")


def test_the_folder_lies_in_the_temporary_folder_by_its_round(made: RunPlace, temp: str) -> None:
    """Given a Round of the command.
    When its folder is asked.
    Then it lies in the system's temporary folder, named by the run and the Round."""
    expected = os.path.join(temp, f"rn-trial-{NAME}-invoice%2F__main__.py-content-1") + os.sep
    assert folder(made, round_of(made)) == expected


@pytest.mark.parametrize("where", ["", "../steering.json"])
def test_a_folder_outside_the_runs_rounds_is_refused(made: RunPlace, where: str) -> None:
    """Given the Rounds' folder itself, or a path out of it.
    When its trial folder is asked.
    Then Wrong is raised, naming it."""
    with pytest.raises(Wrong, match="isn't a Round's folder"):
        folder(made, os.path.join(made.rounds, where))


def test_the_starting_state_holds_the_work_as_committed_without_rns_folder(made: RunPlace) -> None:
    """Given a folder of the Round left there from before, holding a stray file.
    When the starting state is made.
    Then it holds the README and the command, a git clone of the work's branch, and neither rn's
    folder, the draft not committed, nor the stray file."""
    stale = folder(made, round_of(made))
    write_files(stale, {"stray.txt": "old\n"})
    made_at = starting_state(made, round_of(made), run)
    assert sorted(os.listdir(made_at)) == [".git", "README.md", "invoice"]
    with open(os.path.join(made_at, rn_files.COMMAND), encoding="utf-8") as f:
        assert f.read() == "print('invoice')\n"


def test_git_that_cant_clone_cant_run(made: RunPlace) -> None:
    """Given git that can't clone.
    When the starting state is made.
    Then CantRun is raised, naming the folder."""

    def refusing(argv: Sequence[str], cwd: str, env: Mapping[str, str] | None = None) -> Ran:
        return Ran(128, "", "fatal: no room\n")

    with pytest.raises(CantRun, match="can't clone the work's branch into"):
        starting_state(made, round_of(made), refusing)
