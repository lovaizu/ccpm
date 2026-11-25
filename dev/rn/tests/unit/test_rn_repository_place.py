"""The unit cases of repository/place.py: RunPlace, one for each path that follows from a run's
repository and name; `named`, one for each class of the slug, the five-word bound on both sides,
digits, a day of one digit, and each refusal: empty, upper case, a space, letters other than
English, a dash out of place, an underscore, and the user's words as typed; and `of_folder`, one for
each form in which a script is given a run's folder, from the folder it runs in and absolute, and
each refusal: a folder of another form, a near match of the worktree's prefix, a run's folder whose
name differs from its worktree's, and one with no design tree."""

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


def test_a_runs_worktree_lies_under_the_repositorys_claude_worktrees():
    """Given the run 20261120-invoices of the repository /work/invoicer
    When its worktree is asked
    Then it's /work/invoicer/.claude/worktrees/rn-20261120-invoices"""
    run = RunPlace("/work/invoicer", NAME)
    assert same(run.worktree, "/work/invoicer/.claude/worktrees/rn-20261120-invoices")


def test_a_runs_branch_is_rn_and_its_name():
    """Given the run 20261120-invoices
    When its branch is asked
    Then it's rn-20261120-invoices"""
    assert RunPlace("/work/invoicer", NAME).branch == "rn-20261120-invoices"


def test_a_runs_folder_lies_in_its_worktrees_rn_folder():
    """Given the run 20261120-invoices of /work/invoicer
    When its folder is asked
    Then it's its worktree's .rn/20261120-invoices"""
    run = RunPlace("/work/invoicer", NAME)
    assert same(
        run.folder, "/work/invoicer/.claude/worktrees/rn-20261120-invoices/.rn/20261120-invoices"
    )


def test_a_runs_design_tree_lies_in_its_folder():
    """Given the run 20261120-invoices of /work/invoicer
    When its design tree is asked
    Then it's design-tree.json in the run's folder"""
    run = RunPlace("/work/invoicer", NAME)
    assert run.tree == (
        "/work/invoicer/.claude/worktrees/rn-20261120-invoices/.rn/20261120-invoices/"
        "design-tree.json"
    )


def test_a_runs_rounds_lie_in_its_folder():
    """Given the run 20261120-invoices of /work/invoicer
    When the folder of its Rounds is asked
    Then it's rounds in the run's folder"""
    run = RunPlace("/work/invoicer", NAME)
    assert same(
        run.rounds,
        "/work/invoicer/.claude/worktrees/rn-20261120-invoices/.rn/20261120-invoices/rounds",
    )


@pytest.mark.parametrize(
    "slug",
    ["invoices", "overnight-claude-p-queue", "print-invoices-from-their-lines", "v2-readme-typo"],
    ids=["one-word", "issue-62", "five-words", "digits"],
)
def test_a_name_is_the_day_and_the_slug(slug: str):
    """Given a slug of one word, of four as for issue #62's title, of five, the most, or one with
    digits
    When a run is named on 2026-11-20
    Then the name is the day and the slug, joined by -"""
    assert named(DAY, slug) == f"20261120-{slug}"


def test_a_name_writes_a_day_of_one_digit_with_two():
    """Given the day 2026-01-05
    When a run is named
    Then its day is 20260105"""
    assert named(date(2026, 1, 5), "invoices") == "20260105-invoices"


@pytest.mark.parametrize(
    "slug",
    [
        "",
        "print-invoices-from-their-lines-today",
        "Print-Invoices",
        "print invoices",
        "経理-invoices",
        "-invoices",
        "invoices-",
        "print--invoices",
        "print_invoices",
        rn_files.WORDS,
    ],
    ids=[
        "empty",
        "six-words",
        "upper-case",
        "space",
        "not-english",
        "leading-dash",
        "trailing-dash",
        "double-dash",
        "underscore",
        "the-users-words",
    ],
)
def test_a_name_of_other_than_a_short_english_slug_is_refused(slug: str):
    """Given an empty slug, one of six words, with upper case, a space, letters other than
    English, a dash that leads, trails, or doubles, an underscore, or the user's words as typed
    When a run is named
    Then Wrong is raised, naming the slug and the form it takes"""
    with pytest.raises(Wrong, match="lower-case English words joined by -"):
        named(DAY, slug)


def a_run_folder(tmp_path: Any, name: str = NAME) -> tuple[str, str]:
    """A repository's top holding the run's folder with its design tree, and the run's folder."""
    repo = os.path.realpath(str(tmp_path / "invoicer"))
    folder = rn_files.run_folder(repo, name, rn_files.tree([rn_files.plan(name, good=False)]))
    return repo, folder


def test_a_run_folder_given_from_the_folder_the_command_runs_in_is_its_run(tmp_path: Any):
    """Given a repository whose run 20261120-invoices has its design tree
    When of_folder is given .claude/worktrees/rn-20261120-invoices/.rn/20261120-invoices from the
    repository's top
    Then it gives that run of that repository"""
    repo, _ = a_run_folder(tmp_path)
    given = f".claude/worktrees/rn-{NAME}/.rn/{NAME}"
    assert of_folder(repo, given) == RunPlace(repo, NAME)


def test_a_run_folder_given_absolute_is_its_run(tmp_path: Any):
    """Given a repository whose run has its design tree, and another folder the command runs in
    When of_folder is given the run's folder as an absolute path
    Then it gives that run of that repository"""
    repo, folder = a_run_folder(tmp_path)
    elsewhere = str(tmp_path / "elsewhere")
    os.makedirs(elsewhere)
    assert of_folder(elsewhere, folder) == RunPlace(repo, NAME)


def test_a_run_folder_given_with_its_closing_slash_is_its_run(tmp_path: Any):
    """Given a repository whose run has its design tree
    When of_folder is given the run's folder with a closing /
    Then it gives that run of that repository"""
    repo, folder = a_run_folder(tmp_path)
    assert of_folder(repo, folder + "/") == RunPlace(repo, NAME)


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
    [
        f".claude/worktrees/rn2-{NAME}/.rn/{NAME}",
        f".claude/worktrees/{NAME}/.rn/{NAME}",
        f".claude/worktrees/rn-{NAME}/.rn/20261120-other",
        f".claude/worktrees/rn-{NAME}",
        f".rn/{NAME}",
    ],
)
def test_a_folder_of_another_form_is_refused_naming_the_form_it_takes(tmp_path: Any, given: str):
    """Given a repository whose folder of the path holds a design tree, the path near a run's
    folder but of another form: a worktree's prefix other than rn-, none, a run's folder whose name
    differs from its worktree's, the worktree alone, or the run's folder outside a worktree
    When of_folder is given it
    Then Wrong is raised, naming the path"""
    repo = os.path.realpath(str(tmp_path))
    rn_files.write_json(os.path.join(repo, given, "design-tree.json"), rn_files.tree([]))
    with pytest.raises(Wrong) as raised:
        of_folder(repo, given)
    assert given in str(raised.value)
