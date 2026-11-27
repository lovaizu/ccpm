"""The unit cases of repository/trial.py, the folder of the people's starting state in which an
evaluator tries a deliverable: where it lies by its Round, a folder outside the work's Rounds
refused, the work's worktree as it stands cloned there without rn's folder or what git ignores,
one left there made anew, the trials removed, and git that can't clone."""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from typing import Any

import pytest
import rn_files
from fault import CantRun, Wrong
from host import Ran, run
from place import WorkPlace
from repo_files import git, write_files
from repository.trial import folder, removed, starting_state

NAME = "20261126-invoice-from-statement"


@pytest.fixture
def made(tmp_path: Any) -> WorkPlace:
    """The work whose worktree holds its steering and the command committed, and since then a
    draft written, the README changed, a note deleted, and a log that git ignores, none
    committed."""
    repo = rn_files.repository(str(tmp_path / "accounting"))
    held = WorkPlace(rn_files.worktree_of(repo, str(tmp_path / "invoices"), "invoices"), NAME)
    rn_files.committed_steering(held.worktree, NAME, rn_files.steering())
    write_files(held.worktree, {rn_files.COMMAND: "print('invoice')\n"})
    write_files(held.worktree, {"note.md": "old\n", ".gitignore": "*.log\n"})
    git(held.worktree, "add", "-A")
    git(held.worktree, "commit", "-q", "-m", "the command")
    write_files(
        held.worktree, {"draft.md": "not yet\n", "README.md": "# Invoices\n", "run.log": "x\n"}
    )
    os.remove(os.path.join(held.worktree, "note.md"))
    return held


def round_of(work: WorkPlace) -> str:
    return os.path.join(work.rounds, "invoice%2F__main__.py", "content-1")


def test_the_folder_lies_in_the_temporary_folder_by_its_round(made: WorkPlace, temp: str) -> None:
    """Given a Round of the command.
    When its folder is asked.
    Then it lies in the system's temporary folder, named by the work and the Round."""
    expected = os.path.join(temp, f"rn-trial-{NAME}", "invoice%2F__main__.py-content-1") + os.sep
    assert folder(made, round_of(made)) == expected


@pytest.mark.parametrize("where", ["", "../steering.json"])
def test_a_folder_outside_the_rounds_of_the_work_is_refused(made: WorkPlace, where: str) -> None:
    """Given the Rounds' folder itself, or a path out of it.
    When its trial folder is asked.
    Then Wrong is raised, naming it."""
    with pytest.raises(Wrong, match="isn't a Round's folder"):
        folder(made, os.path.join(made.rounds, where))


def test_the_starting_state_holds_the_worktree_as_it_stands_without_rns_folder(
    made: WorkPlace,
) -> None:
    """Given a folder of the Round left there from before, holding a stray file.
    When the starting state is made.
    Then it holds a git clone of the worktree with the draft, the README as changed, and the
    command, and neither rn's folder, the note deleted, the log git ignores, nor the stray file."""
    stale = folder(made, round_of(made))
    write_files(stale, {"stray.txt": "old\n"})
    made_at = starting_state(made, round_of(made), run)
    assert sorted(os.listdir(made_at)) == [".git", ".gitignore", "README.md", "draft.md", "invoice"]
    with open(os.path.join(made_at, "README.md"), encoding="utf-8") as f:
        assert f.read() == "# Invoices\n"
    with open(os.path.join(made_at, rn_files.COMMAND), encoding="utf-8") as f:
        assert f.read() == "print('invoice')\n"


def test_the_trials_of_the_work_are_removed_and_no_others(made: WorkPlace, temp: str) -> None:
    """Given the work's trial made, and another work's whose name starts with the work's.
    When the work's trials are removed.
    Then the work's folder of trials is gone, and the other's stays."""
    starting_state(made, round_of(made), run)
    other = WorkPlace(made.worktree, f"{NAME}-2")
    write_files(folder(other, round_of(other)), {"kept.txt": "kept\n"})
    removed(made)
    assert not os.path.exists(os.path.join(temp, f"rn-trial-{NAME}"))
    assert os.path.isfile(os.path.join(folder(other, round_of(other)), "kept.txt"))
    removed(other)


def test_git_that_cant_clone_cant_run(made: WorkPlace) -> None:
    """Given git that can't clone.
    When the starting state is made.
    Then CantRun is raised, naming the folder."""

    def refusing(argv: Sequence[str], cwd: str, env: Mapping[str, str] | None = None) -> Ran:
        return Ran(128, "", "fatal: no room\n") if argv[1] == "clone" else run(argv, cwd, env)

    with pytest.raises(CantRun, match="can't clone the work's worktree into"):
        starting_state(made, round_of(made), refusing)
