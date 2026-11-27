"""The unit cases of place.py, where the work lies and what it's called: a name from the day and a
slug, each path of the work that follows from its name, the work found from its folder, and each
refusal: a slug of another form, a path of another form, and a folder that isn't there."""

from __future__ import annotations

import os
from datetime import date
from typing import Any

import pytest
from fault import Wrong
from place import WorkPlace, named, of_folder

NAME = "20261126-invoice-from-statement"


def test_the_work_is_named_by_its_day_and_slug() -> None:
    """Given the walkthrough's day and the slug invoice-from-statement.
    When the work is named.
    Then its name is the day as yyyymmdd, then the slug."""
    assert named(date(2026, 11, 26), "invoice-from-statement") == NAME


@pytest.mark.parametrize("slug", ["Invoice", "a-b-c-d-e-f", "", "invoice_from"])
def test_a_slug_of_another_form_is_refused(slug: str) -> None:
    """Given a slug with a capital, of six words, empty, or joined by `_`.
    When the work is named.
    Then Wrong is raised, naming the slug and the form it takes."""
    with pytest.raises(Wrong, match="one to five lower-case English words"):
        named(date(2026, 11, 26), slug)


def test_each_path_of_the_work_follows_from_its_name() -> None:
    """Given the work in the worktree /home/ada/invoices.
    When its paths are asked.
    Then each lies where the architecture's Directory structure names it."""
    work = WorkPlace("/home/ada/invoices", NAME)
    folder = f"/home/ada/invoices/.rn/{NAME}"
    assert (work.folder, work.steering, work.pruner, work.rounds) == (
        folder,
        f"{folder}/steering.json",
        f"{folder}/pruner.json",
        f"{folder}/rounds",
    )


def test_the_work_is_found_from_its_folder_by_a_path_from_the_folder_given(tmp_path: Any) -> None:
    """Given the work's folder in a worktree.
    When it's given by its path from the worktree's top, and by its absolute path.
    Then the work is found each time, with the worktree and the name."""
    work = WorkPlace(str(tmp_path), NAME)
    os.makedirs(work.folder)
    assert (of_folder(work.worktree, f".rn/{NAME}"), of_folder("/", work.folder)) == (work, work)


@pytest.mark.parametrize(
    "folder",
    ["/home/ada/accounting/x", "/home/ada/.rn/BAD NAME", f"/w/.rn/{NAME}/rounds"],
)
def test_a_path_of_another_form_is_refused(folder: str) -> None:
    """Given a path outside the work's folder, a folder not named as rn's work, or a folder inside
    the work's.
    When the work is found from it.
    Then Wrong is raised, naming the form the work's folder takes."""
    with pytest.raises(Wrong, match="isn't the folder of rn's work"):
        of_folder("/", folder)


def test_a_folder_that_is_not_there_is_refused(tmp_path: Any) -> None:
    """Given the path of the work's folder that no one made.
    When the work is found from it.
    Then Wrong is raised, saying no such folder lies there."""
    with pytest.raises(Wrong, match="no such folder"):
        of_folder("/", WorkPlace(str(tmp_path), NAME).folder)
