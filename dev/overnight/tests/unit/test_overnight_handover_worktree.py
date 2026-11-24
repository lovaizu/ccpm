"""The unit cases of handover/worktree.py, where a piece's worktree lies and which branch it's on:
`taken`, of none, one, and several branches and folders of overnight, beside names that nearly
match, and outside a Git repository; and `make`, from the current commit of the person's branch
with changes not committed, of a number of two digits, and of a repository with no commit yet."""

from __future__ import annotations

import os
from typing import Any

import overnight_files
import pytest
from handover.worktree import Refused, Worktree, make, taken
from overnight_files import git, piece_folder

pytestmark = pytest.mark.xfail(strict=True, reason="handover.worktree isn't built yet")


def beside(repo: str, name: str) -> str:
    """The path of the name in the folder that holds the repository."""
    return os.path.join(os.path.dirname(repo), name)


def same(repo: str, folder: str, expected: str) -> bool:
    """Whether the folder, from the repository's root where it's relative, is the one expected."""
    return os.path.realpath(os.path.join(repo, folder)) == os.path.realpath(expected)


# taken


@pytest.mark.supports(
    "test_a_new_piece_takes_the_number_after_the_highest_of_records_branches_and_worktrees"
)
def test_taken_of_a_repository_with_no_branch_or_folder_of_overnight_is_0(repo: str):
    """Given the walkthrough's repository, with no branch or folder of overnight
    When the highest number that a branch or worktree holds is asked
    Then it is 0"""
    assert taken(repo) == 0


@pytest.mark.supports(
    "test_a_new_piece_takes_the_number_after_the_highest_of_records_branches_and_worktrees"
)
def test_taken_of_one_branch_is_its_number(repo: str):
    """Given the repository with the one branch `overnight/5`
    When the highest number that a branch or worktree holds is asked
    Then it is 5"""
    git(repo, "branch", "overnight/5")
    assert taken(repo) == 5


@pytest.mark.supports(
    "test_a_new_piece_takes_the_number_after_the_highest_of_records_branches_and_worktrees"
)
def test_taken_of_one_folder_is_its_number(repo: str):
    """Given the repository with the one folder `../myapp-overnight-7`, which git doesn't know
    When the highest number that a branch or worktree holds is asked
    Then it is 7"""
    os.makedirs(piece_folder(repo, 7))
    assert taken(repo) == 7


@pytest.mark.supports(
    "test_a_new_piece_takes_the_number_after_the_highest_of_records_branches_and_worktrees"
)
@pytest.mark.parametrize(
    ("branches", "folders", "expected"),
    [((3, 12), (9,), 12), ((3,), (12, 9), 12)],
    ids=["a branch highest", "a folder highest"],
)
def test_taken_of_several_is_the_greatest_number_of_either_whatever_its_order_by_name(
    repo: str, branches: tuple[int, ...], folders: tuple[int, ...], expected: int
):
    """Given branches and folders of overnight whose greatest number, 12, comes neither first nor
    last by name, on a branch, or on a folder
    When the highest number that a branch or worktree holds is asked
    Then it is 12"""
    for number in branches:
        git(repo, "branch", f"overnight/{number}")
    for number in folders:
        os.makedirs(piece_folder(repo, number))
    assert taken(repo) == expected


@pytest.mark.supports(
    "test_a_new_piece_takes_the_number_after_the_highest_of_records_branches_and_worktrees"
)
def test_taken_leaves_out_each_branch_and_folder_that_only_nearly_matches(repo: str):
    """Given the branch `overnight/2`, beside branches `overnight/40x`, `overnight-41`,
    `feature/overnight/42`, and `overnight/43/fix`; and the folder `../myapp-overnight-3`, beside
    folders `../myapp2-overnight-50`, `../xmyapp-overnight-51`, `../myapp-overnight-52x`,
    `../myapp-overnight-`, and a file `../myapp-overnight-53`
    When the highest number that a branch or worktree holds is asked
    Then it is 3"""
    for branch in ("overnight/2", "overnight/40x", "overnight-41", "feature/overnight/42"):
        git(repo, "branch", branch)
    git(repo, "branch", "overnight/43/fix")
    for name in (
        "myapp-overnight-3",
        "myapp2-overnight-50",
        "xmyapp-overnight-51",
        "myapp-overnight-52x",
        "myapp-overnight-",
    ):
        os.makedirs(beside(repo, name))
    with open(beside(repo, "myapp-overnight-53"), "w", encoding="utf-8") as f:
        f.write("")
    assert taken(repo) == 3


@pytest.mark.supports("test_a_hand_over_outside_a_git_repository_is_refused_with_gits_words")
def test_taken_outside_a_git_repository_is_refused_with_gits_words(tmp_path: Any):
    """Given a folder that no Git repository holds
    When the highest number that a branch or worktree holds there is asked
    Then Refused is raised, with git's words that it isn't a repository"""
    outside = os.path.join(str(tmp_path), "outside")
    os.makedirs(outside)
    with pytest.raises(Refused, match="(?i)not a git repository"):
        taken(outside)


# make


@pytest.mark.supports(
    "test_a_pieces_changes_stay_on_its_branch_and_the_persons_branch_and_folder_as_they_were"
)
def test_make_adds_the_worktree_beside_from_the_current_commit_and_leaves_the_persons_work(
    repo: str,
):
    """Given the repository on the person's branch `feature`, a commit ahead of main, with a file
    changed and not committed
    When piece 1's worktree is made
    Then it gives `../myapp-overnight-1` on `overnight/1`, a worktree that git lists, at the
    commit of `feature`, without the change; and the person's folder stays on `feature` with its
    change"""
    git(repo, "switch", "-q", "-c", "feature")
    with open(os.path.join(repo, "app.py"), "a", encoding="utf-8") as f:
        f.write("# committed\n")
    git(repo, "commit", "-q", "-am", "A change on feature")
    with open(os.path.join(repo, "app.py"), "a", encoding="utf-8") as f:
        f.write("# not committed\n")
    head = git(repo, "rev-parse", "HEAD")
    given = make(repo, 1)
    folder = piece_folder(repo, 1)
    assert isinstance(given, Worktree)
    assert same(repo, given.folder, folder) and given.branch == "overnight/1"
    assert os.path.realpath(folder) in git(repo, "worktree", "list")
    assert git(folder, "rev-parse", "HEAD") == head
    assert git(folder, "branch", "--show-current") == "overnight/1\n"
    assert git(folder, "status", "--porcelain") == ""
    assert git(repo, "branch", "--show-current") == "feature\n"
    assert git(repo, "status", "--porcelain") == " M app.py\n"


@pytest.mark.supports(
    "test_a_new_piece_takes_the_number_after_the_highest_of_records_branches_and_worktrees"
)
def test_make_of_a_number_of_two_digits_names_its_folder_and_branch_by_it(repo: str):
    """Given the walkthrough's repository
    When piece 10's worktree is made
    Then it gives `../myapp-overnight-10` on `overnight/10`"""
    given = make(repo, 10)
    assert same(repo, given.folder, piece_folder(repo, 10))
    assert given.branch == "overnight/10"


@pytest.mark.supports("test_a_hand_over_outside_a_git_repository_is_refused_with_gits_words")
def test_make_in_a_repository_with_no_commit_is_refused_with_gits_words(tmp_path: Any):
    """Given a repository made with `git init` and no commit yet
    When piece 1's worktree is made
    Then Refused is raised with git's words, and no folder `../myapp-overnight-1` is made"""
    repo = overnight_files.repository(os.path.join(str(tmp_path), "work"), commit=False)
    with pytest.raises(Refused) as refused:
        make(repo, 1)
    assert str(refused.value).strip()
    assert not os.path.exists(piece_folder(repo, 1))
