"""The unit cases of tree/runs.py, each run's name and places and the runs left, through `name`,
`title`, `of`, `here`, and `left`, on a git repository of the test's own."""

from __future__ import annotations

import datetime
import os
from typing import Any

import pytest
from rn_example import HINTS_NAME, WORDS, git
from rn_parts import ANSWERED, NAME, doing, hints, repository, typed, walkthrough
from tree import design
from tree.fault import Wrong
from tree.rounds import Place, folder, keep_place
from tree.runs import Left, Run, here, left, name, of, title

pytestmark = pytest.mark.xfail(strict=True, reason="rn's parts are skeletons, their bodies unbuilt")

DAY = datetime.date(2026, 11, 14)


@pytest.mark.supports(
    "test_up_with_a_request_makes_the_runs_worktree_on_its_branch_with_its_folder"
)
def test_name_is_the_day_and_the_words_lowered_with_dashes():
    """Given the walkthrough's words and 14 November 2026
    When the run's name is asked for
    Then it's 20261114-type-hints-for-invoicer"""
    assert name(WORDS, DAY) == NAME


@pytest.mark.supports(
    "test_up_with_a_request_makes_the_runs_worktree_on_its_branch_with_its_folder"
)
def test_name_keeps_only_letters_and_digits_of_the_words():
    """Given `README, for invoicer 2!`
    When the run's name is asked for
    Then it's 20261114-readme-for-invoicer-2"""
    assert name("README, for invoicer 2!", DAY) == "20261114-readme-for-invoicer-2"


@pytest.mark.parametrize("words", ["", "  ", "!?"])
@pytest.mark.supports(
    "test_up_with_a_request_makes_the_runs_worktree_on_its_branch_with_its_folder"
)
def test_name_refuses_words_with_no_letter_or_digit(words: str):
    """Given empty words, spaces, or marks alone
    When the run's name is asked for
    Then it's refused"""
    with pytest.raises(Wrong):
        name(words, DAY)


@pytest.mark.supports(
    "test_up_with_a_request_makes_the_runs_worktree_on_its_branch_with_its_folder"
)
def test_of_places_the_worktree_the_branch_and_the_folder_of_the_run():
    """Given the repository at /repo
    When the run of the walkthrough's name is asked for
    Then its worktree is /repo/.claude/worktrees/rn-<name>, its branch rn/<name>, and its folder
    .rn/<name> in the worktree"""
    worktree = f"/repo/.claude/worktrees/rn-{NAME}"
    expected = Run(NAME, "/repo", worktree, f"rn/{NAME}", f"{worktree}/.rn/{NAME}")
    assert of("/repo", NAME) == expected


@pytest.mark.supports("test_runs_lists_the_run_paused_with_what_it_was_making_and_where")
def test_title_gives_the_words_as_the_user_reads_them():
    """Given the walkthrough's run
    When its words are asked for
    Then they're `type hints for invoicer`"""
    assert title(of("/repo", NAME)) == WORDS


@pytest.mark.supports("test_the_users_ty_signs_off_the_plan_waiting")
def test_here_is_the_run_of_the_worktree_that_holds_the_folder(tmp_path: Any):
    """Given the walkthrough's run's worktree
    When the run of a folder inside it is asked for
    Then it's that run"""
    root, _ = repository(str(tmp_path))
    run = of(root, NAME)
    git(root, "worktree", "add", "-q", "-b", run.branch, run.worktree)
    assert here(os.path.join(run.worktree, "invoicer")) == run


@pytest.mark.supports("test_ty_with_nothing_waiting_doesnt_load")
def test_here_refuses_a_folder_of_no_runs_worktree(tmp_path: Any):
    """Given the repository's own checkout
    When the run of its root is asked for
    Then it's refused"""
    root, _ = repository(str(tmp_path))
    with pytest.raises(Wrong):
        here(root)


@pytest.mark.supports("test_runs_with_no_run_left_lists_none")
def test_left_with_no_run_is_none(tmp_path: Any):
    """Given a repository with no worktree of a run
    When the runs left are asked for
    Then there are none"""
    root, _ = repository(str(tmp_path))
    assert left(root) == ()


@pytest.mark.supports("test_runs_lists_the_run_paused_with_what_it_was_making_and_where")
def test_left_gives_the_run_with_what_it_makes_and_each_roles_place(tmp_path: Any):
    """Given the walkthrough's run, the hints doing, and the generator's Place at step 4
    When the runs left are asked for
    Then the run is left, making the hints, with the generator at step 4, and nothing waiting"""
    root, _ = repository(str(tmp_path))
    run = of(root, NAME)
    git(root, "worktree", "add", "-q", "-b", run.branch, run.worktree)
    os.makedirs(folder(run.folder, "invoicer/", 1))
    design.save(run.folder, walkthrough(doing(hints(ANSWERED)), typed()))
    keep_place(run.folder, "invoicer/", Place("generator", 4))
    assert left(root) == (Left(run, (HINTS_NAME,), (Place("generator", 4),), ""),)


@pytest.mark.supports("test_runs_lists_each_of_two_runs_left_for_the_user_to_pick")
def test_left_gives_each_run_in_the_order_of_their_names_and_skips_other_worktrees(tmp_path: Any):
    """Given two runs' worktrees and a worktree of the user's own
    When the runs left are asked for
    Then they're the two runs, in the order of their names"""
    root, _ = repository(str(tmp_path))
    names = ("20261114-type-hints-for-invoicer", "20261113-readme-for-invoicer")
    for each in names:
        run = of(root, each)
        git(root, "worktree", "add", "-q", "-b", run.branch, run.worktree)
        os.makedirs(run.folder)
    git(root, "worktree", "add", "-q", "-b", "mine", os.path.join(str(tmp_path), "mine"))
    assert [each.run.name for each in left(root)] == sorted(names)
