"""The unit cases of repository/place.py: RunPlace, one for each path that follows from a run's
repository and name; `named`, one for each class of the goal's words, the five-word bound on both
sides, upper case, characters other than letters and digits, a day of one digit, and the refusal of
words with no letter or digit; and `of_folder`, one for each form in which a script is given a run's
folder, from the folder it runs in and absolute, and each refusal: a folder of another form, a near
match of the worktree's prefix, a run's folder whose name differs from its worktree's, and one with
no design tree; and `made`, one for a run of the words made today, one made the day before, the
latest of several days, each near match of the name, a worktree with no design tree, no worktrees,
and the refusal of words with no letter or digit."""

from __future__ import annotations

import os
from datetime import date
from typing import Any

import pytest
import rn_files
from fault import Wrong
from repository.place import RunPlace, made, named, of_folder

NAME = "20261120-invoices"
DAY = date(2026, 11, 20)


def same(path: str, expected: str) -> bool:
    """Whether the path names the expected one, a folder with or without its closing `/`."""
    return os.path.normpath(path) == os.path.normpath(expected)


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_a_runs_worktree_lies_under_the_repositorys_claude_worktrees():
    """Given the run 20261120-invoices of the repository /work/invoicer
    When its worktree is asked
    Then it's /work/invoicer/.claude/worktrees/rn-20261120-invoices"""
    run = RunPlace("/work/invoicer", NAME)
    assert same(run.worktree, "/work/invoicer/.claude/worktrees/rn-20261120-invoices")


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_a_runs_branch_is_rn_and_its_name():
    """Given the run 20261120-invoices
    When its branch is asked
    Then it's rn-20261120-invoices"""
    assert RunPlace("/work/invoicer", NAME).branch == "rn-20261120-invoices"


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_a_runs_folder_lies_in_its_worktrees_rn_folder():
    """Given the run 20261120-invoices of /work/invoicer
    When its folder is asked
    Then it's its worktree's .rn/20261120-invoices"""
    run = RunPlace("/work/invoicer", NAME)
    assert same(
        run.folder, "/work/invoicer/.claude/worktrees/rn-20261120-invoices/.rn/20261120-invoices"
    )


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
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


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
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


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_a_name_takes_the_first_five_words_of_more():
    """Given the walkthrough's words, of more than five words
    When a run is named on 2026-11-20
    Then the name is the day and the first five words, joined by -"""
    assert named(DAY, rn_files.WORDS) == "20261120-a-command-with-which-the"


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_a_name_takes_each_of_five_words():
    """Given words of five words exactly
    When a run is named
    Then each word stands in the name"""
    assert (
        named(DAY, "print invoices from their lines") == "20261120-print-invoices-from-their-lines"
    )


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_a_name_leaves_out_the_sixth_word():
    """Given words of six words
    When a run is named
    Then the sixth word stands nowhere in the name"""
    assert named(DAY, "print invoices from their lines today") == (
        "20261120-print-invoices-from-their-lines"
    )


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_a_name_of_one_word_is_that_word():
    """Given words of one word
    When a run is named
    Then the name is the day and that word"""
    assert named(DAY, "invoices") == "20261120-invoices"


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_a_name_is_lower_case():
    """Given words in upper and mixed case
    When a run is named
    Then the name holds them in lower case"""
    assert named(DAY, "Print INVOICES") == "20261120-print-invoices"


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_a_name_leaves_out_each_character_other_than_a_letter_or_a_digit():
    """Given words with an apostrophe, a comma, a slash, and an exclamation mark, and a digit
    When a run is named
    Then each of those characters is left out and the digit kept"""
    assert named(DAY, "Fix the README's typo, v2/now!") == "20261120-fix-the-readmes-typo-v2now"


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_a_name_joins_words_split_by_more_than_one_space():
    """Given words split by tabs, newlines, and several spaces
    When a run is named
    Then the words are joined by one - each"""
    assert named(DAY, "  print\tinvoices \n now ") == "20261120-print-invoices-now"


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
def test_a_name_writes_a_day_of_one_digit_with_two():
    """Given the day 2026-01-05
    When a run is named
    Then its day is 20260105"""
    assert named(date(2026, 1, 5), "invoices") == "20260105-invoices"


@pytest.mark.supports(
    "test_a_request_makes_the_runs_worktree_and_its_design_tree_with_the_goal_as_put"
)
@pytest.mark.parametrize("words", ["", "   ", "!!! ... ?"])
def test_a_name_of_words_with_no_letter_or_digit_is_refused(words: str):
    """Given words with no letter or digit
    When a run is named
    Then Wrong is raised, saying that /rn:on takes what the user wants in words"""
    with pytest.raises(Wrong, match="/rn:on"):
        named(DAY, words)


def a_run_folder(tmp_path: Any, name: str = NAME) -> tuple[str, str]:
    """A repository's top holding the run's folder with its design tree, and the run's folder."""
    repo = os.path.realpath(str(tmp_path / "invoicer"))
    folder = rn_files.run_folder(repo, name, rn_files.tree([rn_files.plan(name, good=False)]))
    return repo, folder


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_a_run_folder_given_from_the_folder_the_command_runs_in_is_its_run(tmp_path: Any):
    """Given a repository whose run 20261120-invoices has its design tree
    When of_folder is given .claude/worktrees/rn-20261120-invoices/.rn/20261120-invoices from the
    repository's top
    Then it gives that run of that repository"""
    repo, _ = a_run_folder(tmp_path)
    given = f".claude/worktrees/rn-{NAME}/.rn/{NAME}"
    assert of_folder(repo, given) == RunPlace(repo, NAME)


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_a_run_folder_given_absolute_is_its_run(tmp_path: Any):
    """Given a repository whose run has its design tree, and another folder the command runs in
    When of_folder is given the run's folder as an absolute path
    Then it gives that run of that repository"""
    repo, folder = a_run_folder(tmp_path)
    elsewhere = str(tmp_path / "elsewhere")
    os.makedirs(elsewhere)
    assert of_folder(elsewhere, folder) == RunPlace(repo, NAME)


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_a_run_folder_given_with_its_closing_slash_is_its_run(tmp_path: Any):
    """Given a repository whose run has its design tree
    When of_folder is given the run's folder with a closing /
    Then it gives that run of that repository"""
    repo, folder = a_run_folder(tmp_path)
    assert of_folder(repo, folder + "/") == RunPlace(repo, NAME)


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
def test_a_run_folder_with_no_design_tree_is_refused(tmp_path: Any):
    """Given a repository holding a run's folder of the right form with no design tree
    When of_folder is given it
    Then Wrong is raised, naming the path"""
    repo = os.path.realpath(str(tmp_path))
    folder = rn_files.folder_of(repo, NAME)
    os.makedirs(folder)
    with pytest.raises(Wrong, match=NAME):
        of_folder(repo, folder)


@pytest.mark.supports("test_a_new_conversation_picks_up_the_run_from_its_files")
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


# made: the run that a request's words named on some day.


@pytest.mark.supports("test_an_answer_after_the_request_goes_into_the_run_the_request_made")
def test_the_run_named_from_the_words_today_is_the_run_made(tmp_path: Any):
    """Given a repository whose run 20261120-invoices has its design tree
    When made is asked for the run of the words `Invoices`
    Then it gives that run"""
    repo, _ = a_run_folder(tmp_path)
    assert made(repo, "Invoices") == RunPlace(repo, NAME)


@pytest.mark.supports("test_an_answer_after_the_request_goes_into_the_run_the_request_made")
def test_the_run_named_from_the_words_on_an_earlier_day_is_the_run_made(tmp_path: Any):
    """Given a repository whose run 20261119-invoices, named the day before, has its design tree,
    as a request made before midnight and answered after it leaves it
    When made is asked for the run of the words `Invoices`
    Then it gives that run"""
    repo, _ = a_run_folder(tmp_path, "20261119-invoices")
    assert made(repo, "Invoices") == RunPlace(repo, "20261119-invoices")


@pytest.mark.supports("test_an_answer_after_the_request_goes_into_the_run_the_request_made")
def test_of_runs_named_from_the_words_on_several_days_the_latest_days_is_the_run_made(
    tmp_path: Any,
):
    """Given a repository whose runs 20261101-invoices, 20261120-invoices, and 20261105-invoices
    each have their design tree
    When made is asked for the run of the words `Invoices`
    Then it gives 20261120-invoices, the latest day's"""
    repo, _ = a_run_folder(tmp_path, "20261101-invoices")
    a_run_folder(tmp_path, "20261120-invoices")
    a_run_folder(tmp_path, "20261105-invoices")
    assert made(repo, "Invoices") == RunPlace(repo, "20261120-invoices")


@pytest.mark.supports("test_an_answer_after_the_request_goes_into_the_run_the_request_made")
@pytest.mark.parametrize(
    "name",
    ["20261120-invoices-due", "20261120-invoice", "2026112-invoices", "x20261120-invoices"],
    ids=["more-words", "fewer-letters", "short-day", "not-a-day"],
)
def test_a_run_whose_name_nearly_matches_the_words_isnt_the_run_made(tmp_path: Any, name: str):
    """Given a repository whose only run's name nearly matches the words `Invoices`: another goal
    that starts with them, one a letter short, a day of seven digits, or one that isn't a day
    When made is asked for the run of the words
    Then it gives None"""
    repo, _ = a_run_folder(tmp_path, name)
    assert made(repo, "Invoices") is None


@pytest.mark.supports("test_an_answer_after_the_request_goes_into_the_run_the_request_made")
def test_a_worktree_of_the_words_with_no_design_tree_isnt_the_run_made(tmp_path: Any):
    """Given a repository holding the worktree of 20261120-invoices with no design tree, as a
    refused `new` may leave it
    When made is asked for the run of the words `Invoices`
    Then it gives None"""
    repo = os.path.realpath(str(tmp_path))
    os.makedirs(rn_files.worktree_of(repo, NAME))
    assert made(repo, "Invoices") is None


@pytest.mark.supports("test_an_answer_after_the_request_goes_into_the_run_the_request_made")
def test_a_repository_with_no_worktrees_has_no_run_made(tmp_path: Any):
    """Given a repository with no .claude/worktrees/
    When made is asked for the run of the words `Invoices`
    Then it gives None"""
    assert made(os.path.realpath(str(tmp_path)), "Invoices") is None


@pytest.mark.supports("test_an_answer_after_the_request_goes_into_the_run_the_request_made")
def test_made_for_words_with_no_letter_or_digit_is_refused(tmp_path: Any):
    """Given a repository, and words with no letter or digit
    When made is asked for the run of the words
    Then Wrong is raised, saying that /rn:on takes what the user wants in words"""
    with pytest.raises(Wrong, match="/rn:on"):
        made(os.path.realpath(str(tmp_path)), "!!!")
