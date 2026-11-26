"""The unit cases of place.py, where a run lies and what it's called: a name from the day and a
slug, each path of a run that follows from its name, a run found from its folder, and each
refusal: a slug of another form, a path of another form, and a folder that isn't there."""

from __future__ import annotations

import os
from datetime import date
from typing import Any

import pytest
from fault import Wrong
from place import RunPlace, named, of_folder

NAME = "20261126-invoice-from-statement"


def test_a_run_is_named_by_its_day_and_slug() -> None:
    """Given the walkthrough's day and the slug invoice-from-statement.
    When the run is named.
    Then its name is the day as yyyymmdd, then the slug."""
    assert named(date(2026, 11, 26), "invoice-from-statement") == NAME


@pytest.mark.parametrize("slug", ["Invoice", "a-b-c-d-e-f", "", "invoice_from"])
def test_a_slug_of_another_form_is_refused(slug: str) -> None:
    """Given a slug with a capital, of six words, empty, or joined by `_`.
    When the run is named.
    Then Wrong is raised, naming the slug and the form it takes."""
    with pytest.raises(Wrong, match="one to five lower-case English words"):
        named(date(2026, 11, 26), slug)


def test_each_path_of_a_run_follows_from_its_name() -> None:
    """Given a run of the repository /work/accounting.
    When its paths are asked.
    Then each lies where the architecture's Directory structure names it."""
    run = RunPlace("/work/accounting", NAME)
    worktree = f"/work/accounting/.claude/worktrees/rn-{NAME}"
    assert (run.branch, run.worktree, run.folder, run.steering, run.pruner, run.rounds) == (
        f"rn-{NAME}",
        worktree,
        f"{worktree}/.rn/{NAME}",
        f"{worktree}/.rn/{NAME}/steering.json",
        f"{worktree}/.rn/{NAME}/pruner.json",
        f"{worktree}/.rn/{NAME}/rounds",
    )


def test_a_run_is_found_from_its_folder_by_a_path_from_the_folder_given(tmp_path: Any) -> None:
    """Given a run's folder in a repository.
    When it's given by its path from the worktree's top.
    Then the run is found, with the repository and the name."""
    run = RunPlace(str(tmp_path), NAME)
    os.makedirs(run.folder)
    assert of_folder(run.worktree, f".rn/{NAME}") == run


@pytest.mark.parametrize(
    "folder", ["/work/accounting/.rn/x", f"/w/.claude/worktrees/rn-{NAME}/.rn/other"]
)
def test_a_path_of_another_form_is_refused(folder: str) -> None:
    """Given a path outside a run's worktree, or a folder whose name differs from its worktree's.
    When the run is found from it.
    Then Wrong is raised, naming the form a run's folder takes."""
    with pytest.raises(Wrong, match="isn't a run's folder"):
        of_folder("/", folder)


def test_a_folder_that_is_not_there_is_refused(tmp_path: Any) -> None:
    """Given the path of a run's folder that no one made.
    When the run is found from it.
    Then Wrong is raised, saying no such folder lies there."""
    with pytest.raises(Wrong, match="no such folder"):
        of_folder("/", RunPlace(str(tmp_path), NAME).folder)
