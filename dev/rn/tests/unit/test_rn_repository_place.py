"""The unit cases of repository/place.py: RunPlace, the paths that follow from a run's repository
and name; `named`, of a slug of five words, the most, and the refusal of one of six; and
`of_folder`, of a run's folder from the folder it runs in and absolute, and each refusal: a folder
of another form, a run's folder whose name differs from its worktree's, and one with no design
tree."""

from __future__ import annotations

import os
from datetime import date
from typing import Any

import pytest
import rn_files
from fault import Wrong
from repository.place import RunPlace, named, of_folder

NAME = "20261120-invoices"
DAY = date(2026, 11, 20)


def same(path: str, expected: str) -> bool:
    """Whether the path names the expected one, a folder with or without its closing `/`."""
    return os.path.normpath(path) == os.path.normpath(expected)


def test_a_runs_paths_follow_from_its_repository_and_name():
    """Given the run 20261120-invoices of the repository /work/invoicer
    When its worktree, branch, folder, design tree, pruner's result, and folder of Rounds are asked
    Then they're /work/invoicer/.claude/worktrees/rn-20261120-invoices, rn-20261120-invoices, its
    worktree's .rn/20261120-invoices, and design-tree.json, pruner.json, and rounds in that
    folder"""
    run = RunPlace("/work/invoicer", NAME)
    folder = "/work/invoicer/.claude/worktrees/rn-20261120-invoices/.rn/20261120-invoices"
    assert same(run.worktree, "/work/invoicer/.claude/worktrees/rn-20261120-invoices")
    assert run.branch == "rn-20261120-invoices"
    assert same(run.folder, folder)
    assert run.tree == f"{folder}/design-tree.json"
    assert run.pruner == f"{folder}/pruner.json"
    assert same(run.rounds, f"{folder}/rounds")


def test_a_name_is_the_day_and_a_slug_of_up_to_five_words():
    """Given a slug of five words, the most
    When a run is named on 2026-11-20
    Then the name is the day and the slug, joined by -"""
    assert (
        named(DAY, "print-invoices-from-their-lines") == "20261120-print-invoices-from-their-lines"
    )


def test_a_name_of_other_than_a_short_english_slug_is_refused():
    """Given a slug of six words, one past the most
    When a run is named
    Then Wrong is raised, naming the slug and the form it takes"""
    with pytest.raises(Wrong, match="print-invoices-from-their-lines-today.*lower-case English"):
        named(DAY, "print-invoices-from-their-lines-today")


def a_run_folder(tmp_path: Any, name: str = NAME) -> tuple[str, str]:
    """A repository's top holding the run's folder with its design tree, and the run's folder."""
    repo = os.path.realpath(str(tmp_path / "invoicer"))
    folder = rn_files.run_folder(repo, name, rn_files.tree([rn_files.plan(name, good=False)]))
    return repo, folder


def test_a_run_folder_given_from_the_folder_the_command_runs_in_or_absolute_is_its_run(
    tmp_path: Any,
):
    """Given a repository whose run 20261120-invoices has its design tree, and another folder
    When of_folder is given .claude/worktrees/rn-20261120-invoices/.rn/20261120-invoices from the
    repository's top, and the run's folder as an absolute path from the other folder
    Then each gives that run of that repository"""
    repo, folder = a_run_folder(tmp_path)
    elsewhere = str(tmp_path / "elsewhere")
    os.makedirs(elsewhere)
    given = f".claude/worktrees/rn-{NAME}/.rn/{NAME}"
    assert of_folder(repo, given) == RunPlace(repo, NAME)
    assert of_folder(elsewhere, folder) == RunPlace(repo, NAME)


def test_a_run_folder_with_no_design_tree_is_refused(tmp_path: Any):
    """Given a repository holding a run's folder of the right form with no design tree
    When of_folder is given it
    Then Wrong is raised, naming the path"""
    repo = os.path.realpath(str(tmp_path))
    folder = rn_files.folder_of(repo, NAME)
    os.makedirs(folder)
    with pytest.raises(Wrong, match=NAME):
        of_folder(repo, folder)


@pytest.mark.parametrize(
    "given",
    [f".rn/{NAME}", f".claude/worktrees/rn-{NAME}/.rn/20261120-other"],
    ids=["outside-a-worktree", "names-apart"],
)
def test_a_folder_of_another_form_is_refused_naming_the_form_it_takes(tmp_path: Any, given: str):
    """Given a repository whose folder of the path holds a design tree, the path near a run's
    folder but of another form: the run's folder outside a worktree, or a run's folder whose name
    differs from its worktree's
    When of_folder is given it
    Then Wrong is raised, naming the path"""
    repo = os.path.realpath(str(tmp_path))
    rn_files.write_json(os.path.join(repo, given, "design-tree.json"), rn_files.tree([]))
    with pytest.raises(Wrong) as raised:
        of_folder(repo, given)
    assert given in str(raised.value)
