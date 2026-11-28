"""The unit cases of repository/todo.py: each line marked `TODO:` that the work adds, committed on
its branch, changed in the worktree, or in a file not yet added, found with its path and line; a
mark that the default branch already holds, one in `.rn/`, and words that only name the mark,
passed over; and a worktree whose remote names no default branch."""

from __future__ import annotations

import os
from typing import Any

import pytest
import rn_files
from fault import Missing
from host import run
from place import WorkPlace
from repo_files import git, write_files
from repository.todo import left

NAME = "20261126-invoice-from-statement"


@pytest.fixture
def made(tmp_path: Any) -> WorkPlace:
    """The work in the user's repository with origin, in its own worktree on the work's branch."""
    return rn_files.work_with_origin(str(tmp_path), NAME)


def committed(work: WorkPlace, files: dict[str, str]) -> None:
    write_files(work.worktree, files)
    git(work.worktree, "add", "-A")
    git(work.worktree, "commit", "-q", "-m", "invoice")


def test_each_todo_the_work_adds_is_found_with_its_place(made: WorkPlace) -> None:
    """Given a TODO committed on the work's branch, one changed in the worktree since, and one in a
    file not yet added.
    When the TODOs left are asked.
    Then each is given as its path and line, with the line's words."""
    committed(made, {"README.md": "# Accounting\n\nTODO: how to print one.\n"})
    committed(made, {"docs/guide.md": "# Guide\n"})
    write_files(made.worktree, {"docs/guide.md": "# Guide\n\nTODO: the rules.\n"})
    write_files(made.worktree, {"invoice/__main__.py": "# TODO: print it\n"})
    assert left(made.worktree, run) == [
        "README.md:3: TODO: how to print one.",
        "docs/guide.md:3: TODO: the rules.",
        "invoice/__main__.py:1: # TODO: print it",
    ]


def test_a_todo_that_isnt_the_works_is_passed_over(made: WorkPlace) -> None:
    """Given a mark that the default branch already holds, one in the work's folder, and words that
    only name the mark.
    When the TODOs left are asked.
    Then there are none, as only what the work adds to its deliverables is left to fill."""
    top = os.path.join(os.path.dirname(made.worktree), "accounting")
    committed(WorkPlace(top, NAME), {"NOTES.md": "TODO: an old note\n"})
    git(top, "push", "-q", "origin", "main")
    git(made.worktree, "fetch", "-q", "origin")
    git(made.worktree, "merge", "-q", "origin/main")
    write_files(made.folder, {"notes.md": "TODO: ask the accountants\n"})
    committed(made, {"README.md": "# Accounting\n\nEach TODO is filled, and no `TODO:` is left.\n"})
    assert left(made.worktree, run) == []


def test_a_remote_that_names_no_default_branch_is_missing(made: WorkPlace) -> None:
    """Given the worktree whose remote names no default branch.
    When the TODOs left are asked.
    Then Missing is raised, saying how to name it."""
    git(made.worktree, "remote", "set-head", "origin", "--delete")
    with pytest.raises(Missing, match="git remote set-head origin --auto"):
        left(made.worktree, run)
