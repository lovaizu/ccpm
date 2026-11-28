"""The unit cases of repository/worktree.py: `top`, the worktree a folder lies in, and none;
`new`, which makes the work's folder at the worktree's top, and work of the name already there;
and `works` with `left`, the work in the worktree newest first, the work ended left out, the work
of an earlier rn whose steering is in another form left out, the work with no steering yet kept, a
folder of another name passed over, none in a folder outside git, and a steering that isn't JSON."""

from __future__ import annotations

import os
from typing import Any

import pytest
import rn_files
from fault import Missing, Wrong
from host import run
from place import WorkPlace
from repo_files import write_files
from repository.worktree import left, new, top, works

NAME = "20261126-invoice-from-statement"
SCHEMA = os.path.join(rn_files.SCHEMAS, "steering.schema.json")
OTHER = "20261127-invoice-rules"


@pytest.fixture
def worktree(tmp_path: Any) -> str:
    """The user's repository, checked out on the work's branch."""
    return rn_files.repository(str(tmp_path / "accounting"), "invoices")


def test_the_top_is_the_worktree_a_folder_lies_in(worktree: str) -> None:
    """Given a folder inside the worktree.
    When its top is asked.
    Then it's the worktree."""
    inner = os.path.join(worktree, "docs")
    os.makedirs(inner)
    assert top(inner, run) == worktree


def test_a_folder_outside_git_has_no_top(tmp_path: Any) -> None:
    """Given a folder that lies in no git worktree.
    When its top is asked.
    Then Missing is raised."""
    with pytest.raises(Missing, match="lies in no git worktree"):
        top(str(tmp_path), run)


def test_the_work_is_made_at_the_top_of_the_worktree(worktree: str) -> None:
    """Given the worktree.
    When the work is made in it.
    Then its folder lies there empty."""
    made = new(WorkPlace(worktree, NAME))
    assert os.listdir(made.folder) == []


def test_work_of_a_name_already_taken_is_refused(worktree: str) -> None:
    """Given the work made in the worktree.
    When work of the same name is made there again.
    Then Wrong is raised, saying to pick it up."""
    new(WorkPlace(worktree, NAME))
    with pytest.raises(Wrong, match="pick it up with /rn:up"):
        new(WorkPlace(worktree, NAME))


def test_the_work_of_the_worktree_is_found_newest_first(worktree: str) -> None:
    """Given a piece of work, a later one with no steering yet, an ended one, one of an earlier rn
    whose steering is in another form, and a folder of another name in `.rn/`.
    When each piece of work, and each with something left to do, is asked.
    Then the later comes first, the ended one and the earlier rn's are left out of what's left, and
    the other folder is passed over."""
    first = new(WorkPlace(worktree, NAME))
    rn_files.write_json(first.steering, rn_files.steering())
    later = new(WorkPlace(worktree, OTHER))
    ended = new(WorkPlace(worktree, "20261125-print"))
    rn_files.write_json(ended.steering, rn_files.steering(paths=(), stage="inspected"))
    earlier = new(WorkPlace(worktree, "20261124-receipts"))
    rn_files.write_json(earlier.steering, {"ost": {"target": "O1"}, "state": {"steps": []}})
    write_files(os.path.join(worktree, ".rn", "notes"), {"a.md": "a\n"})
    assert works(worktree, run) == [later, first, ended, earlier]
    assert left(worktree, run, SCHEMA) == [later, first]


def test_a_worktree_with_no_work_holds_none(worktree: str, tmp_path: Any) -> None:
    """Given a worktree with no `.rn/`, and a folder outside git.
    When the work is asked.
    Then there are none."""
    assert works(worktree, run) == []
    assert works(str(tmp_path), run) == []


def test_a_steering_that_is_not_json_is_refused(worktree: str) -> None:
    """Given the work whose steering isn't JSON.
    When the work with something left to do is asked.
    Then Wrong is raised, naming its path."""
    made = new(WorkPlace(worktree, NAME))
    write_files(made.folder, {"steering.json": "{"})
    with pytest.raises(Wrong, match="steering.json: isn't JSON"):
        left(worktree, run, SCHEMA)
