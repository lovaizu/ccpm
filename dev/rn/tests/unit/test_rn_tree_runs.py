"""The unit cases of tree/runs.py, which decides what makes a run of rn: its name from the goal's
words and the date, rn's worktree of it, its branch and folder, and which runs are left. The cases
take each class of words, a name made or none, a run of that name left or not, and a folder in a
run's worktree, at the root, or in no repository, with no run, one, and two left."""

from __future__ import annotations

import os
import re
from typing import Any

import pytest
from fault import Missing, Wrong
from tree import runs

from dev.rn.tests.unit import rn_data as d

pytestmark = pytest.mark.xfail(strict=True, reason="tree/runs.py has empty bodies")


@pytest.mark.supports("test_a_request_starts_a_run_anew_with_the_tree_keepers_start_first")
def test_a_run_started_has_its_worktree_branch_and_folder(tmp_path: Any) -> None:
    """Given: a repository with no run of rn.
    When: a run starts for the words "type hints for invoicer" on 20261115.
    Then: its name is the date and the words in lower case joined by hyphens, its worktree lies in
    .claude/worktrees/rn-<name>/ on a branch of its own, and its folder .rn/<name>/ is made in
    it."""
    repo = d.repository(str(tmp_path))
    run = runs.start(repo, "type hints for invoicer", d.TODAY)
    assert run.name == d.NAME
    assert run.worktree == os.path.join(repo, ".claude", "worktrees", f"rn-{d.NAME}")
    assert run.folder == os.path.join(run.worktree, ".rn", d.NAME)
    assert os.path.isdir(run.folder)
    assert d.git(run.worktree, "branch", "--show-current").strip() == run.branch
    assert run.branch != "main"


@pytest.mark.supports("test_a_request_starts_a_run_anew_with_the_tree_keepers_start_first")
def test_words_with_capitals_and_marks_make_a_name_of_lower_case_and_hyphens(tmp_path: Any) -> None:
    """Given: a repository with no run of rn.
    When: a run starts for the words "Type hints, for invoicer!".
    Then: its name holds only lower case letters, digits, and hyphens, after the date."""
    run = runs.start(d.repository(str(tmp_path)), "Type hints, for invoicer!", d.TODAY)
    assert re.fullmatch(rf"{d.TODAY}-[a-z0-9]+(-[a-z0-9]+)*", run.name)


@pytest.mark.supports("test_tree_py_refuses_a_run_whose_name_a_run_left_holds")
@pytest.mark.parametrize("words", ["", "   ", "!?"])
def test_words_that_make_no_name_are_refused(tmp_path: Any, words: str) -> None:
    """Given: a repository with no run of rn.
    When: a run starts for words with no letter or digit.
    Then: it's refused, naming the words, and no worktree is made."""
    repo = d.repository(str(tmp_path))
    with pytest.raises(Wrong):
        runs.start(repo, words, d.TODAY)
    assert not os.path.exists(os.path.join(repo, ".claude", "worktrees"))


@pytest.mark.supports("test_tree_py_refuses_a_run_whose_name_a_run_left_holds")
def test_a_run_whose_name_a_run_left_holds_is_refused(tmp_path: Any) -> None:
    """Given: a run of "type hints for invoicer" started today, its worktree still there.
    When: a run starts for the same words on the same day.
    Then: it's refused, naming the run left."""
    repo = d.repository(str(tmp_path))
    runs.start(repo, "type hints for invoicer", d.TODAY)
    with pytest.raises(Wrong, match=d.NAME):
        runs.start(repo, "type hints for invoicer", d.TODAY)


@pytest.mark.supports("test_a_request_starts_a_run_anew_with_the_tree_keepers_start_first")
def test_a_run_started_in_no_repository_is_missing_it(tmp_path: Any) -> None:
    """Given: a folder that lies in no git repository.
    When: a run starts there.
    Then: it's refused as missing a repository."""
    with pytest.raises(Missing):
        runs.start(str(tmp_path), "type hints for invoicer", d.TODAY)


@pytest.mark.supports("test_up_alone_in_the_runs_worktree_picks_up_where_it_stopped")
def test_a_folder_in_a_runs_worktree_gives_that_run(tmp_path: Any) -> None:
    """Given: rn's worktree of a run.
    When: the run of its folder, and of a folder within it, is asked.
    Then: each gives the run."""
    run = d.run_of(d.repository(str(tmp_path)))
    assert runs.of_folder(run.worktree) == run
    assert runs.of_folder(os.path.join(run.worktree, "invoicer")) == run


@pytest.mark.supports("test_a_request_starts_a_run_anew_with_the_tree_keepers_start_first")
def test_the_root_gives_no_run(tmp_path: Any) -> None:
    """Given: a repository with rn's worktree of a run.
    When: the run of the repository's root is asked.
    Then: it gives none."""
    repo = d.repository(str(tmp_path))
    d.run_of(repo)
    assert runs.of_folder(repo) is None


@pytest.mark.supports("test_a_request_starts_a_run_anew_with_the_tree_keepers_start_first")
def test_a_worktree_that_isnt_rns_gives_no_run(tmp_path: Any) -> None:
    """Given: a worktree of the repository that rn didn't make.
    When: the run of its folder is asked.
    Then: it gives none."""
    repo = d.repository(str(tmp_path))
    other = os.path.join(repo, ".claude", "worktrees", "mine")
    d.git(repo, "worktree", "add", "-q", "-b", "mine", other)
    assert runs.of_folder(other) is None


@pytest.mark.supports("test_up_alone_in_the_runs_worktree_picks_up_where_it_stopped")
def test_a_folder_in_no_repository_is_missing_it(tmp_path: Any) -> None:
    """Given: a folder that lies in no git repository.
    When: its run, and the runs left, are asked.
    Then: each is refused as missing a repository."""
    with pytest.raises(Missing):
        runs.of_folder(str(tmp_path))
    with pytest.raises(Missing):
        runs.left(str(tmp_path))


@pytest.mark.supports("test_up_alone_with_no_run_left_says_so_and_starts_no_role")
def test_no_run_left_gives_none(tmp_path: Any) -> None:
    """Given: a repository with no run of rn.
    When: the runs left are asked.
    Then: it gives none."""
    assert runs.left(d.repository(str(tmp_path))) == ()


@pytest.mark.supports("test_up_alone_at_the_root_picks_up_the_one_run_left")
def test_one_run_left_gives_it_from_the_root_or_its_worktree(tmp_path: Any) -> None:
    """Given: a repository with one run of rn, and a worktree that isn't rn's.
    When: the runs left are asked from the root and from the run's worktree.
    Then: each gives that run alone."""
    repo = d.repository(str(tmp_path))
    run = d.run_of(repo)
    d.git(repo, "worktree", "add", "-q", "-b", "mine", os.path.join(tmp_path, "mine"))
    assert runs.left(repo) == (run,)
    assert runs.left(run.worktree) == (run,)


@pytest.mark.supports("test_up_alone_with_two_runs_left_asks_which")
def test_two_runs_left_give_both_by_their_names(tmp_path: Any) -> None:
    """Given: a repository with two runs of rn.
    When: the runs left are asked.
    Then: it gives both, in the order of their names."""
    repo = d.repository(str(tmp_path))
    second = d.run_of(repo, f"{d.TODAY}-a-readme-for-invoicer")
    first = d.run_of(repo)
    assert runs.left(repo) == tuple(sorted((first, second), key=lambda r: r.name))
