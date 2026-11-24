"""The unit cases of handover/number.py, which number a new piece takes: `next_number`, of a
repository with nothing of overnight, of the records' highest above, below, and equal to that of
the branches and folders, and outside a Git repository."""

from __future__ import annotations

import os
from typing import Any

import pytest
from handover.number import next_number
from handover.worktree import Refused
from overnight_files import git, piece_folder

pytestmark = pytest.mark.xfail(strict=True, reason="handover.number isn't built yet")


@pytest.mark.supports(
    "test_the_walkthroughs_three_pieces_go_on_through_the_limit_and_show_done_in_a_later_session"
)
def test_the_first_piece_of_a_repository_takes_1(repo: str):
    """Given the walkthrough's repository, with no record, branch, or folder of overnight
    When the next piece's number is asked
    Then it is 1"""
    assert next_number(repo) == 1


@pytest.mark.supports(
    "test_a_new_piece_takes_the_number_after_the_highest_of_records_branches_and_worktrees"
)
@pytest.mark.parametrize(
    ("record", "branch", "expected"),
    [(9, 5, 10), (4, 7, 8), (6, 6, 7)],
    ids=["a record highest", "a branch highest", "both equal"],
)
def test_the_next_piece_takes_one_more_than_the_highest_of_records_branches_and_folders(
    repo: str, record: int, branch: int, expected: int
):
    """Given a record folder `.overnight/20261120-<n>` of an earlier day, a branch
    `overnight/<m>`, and a folder `../myapp-overnight-2`, where the record's number is above,
    below, or equal to the branch's
    When the next piece's number is asked
    Then it is one more than the highest of them"""
    os.makedirs(os.path.join(repo, ".overnight", f"20261120-{record}"))
    git(repo, "branch", f"overnight/{branch}")
    os.makedirs(piece_folder(repo, 2))
    assert next_number(repo) == expected


@pytest.mark.supports("test_a_hand_over_outside_a_git_repository_is_refused_with_gits_words")
def test_the_next_number_outside_a_git_repository_is_refused_with_gits_words(tmp_path: Any):
    """Given a folder that no Git repository holds
    When the next piece's number there is asked
    Then Refused is raised, with git's words that it isn't a repository"""
    outside = os.path.join(str(tmp_path), "outside")
    os.makedirs(outside)
    with pytest.raises(Refused, match="(?i)not a git repository"):
        next_number(outside)
