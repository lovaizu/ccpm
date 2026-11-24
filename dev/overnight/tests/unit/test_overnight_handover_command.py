"""The unit cases of handover/command.py, handover.py's command line: `main`, of the walkthrough's
piece, of one tool, of tools written with commas and no spaces, of a rule that holds a space, of a
number of two digits; and each refusal: no prompt, no tool, or only commas, outside a Git
repository, and where git can't make the worktree."""

from __future__ import annotations

import os
from typing import Any

import overnight_files
import pytest
from claude_code import claude_double
from handover.command import main
from overnight_files import PROMPT, TOOLS, TOOLS_LINE, git, handover_lines

pytestmark = pytest.mark.xfail(strict=True, reason="handover.command isn't built yet")


def held(stand_in: str, number: int = 1) -> None:
    """Gives Claude Code a run of the piece of the number that it holds until the case ends."""
    claude_double.plays(stand_in, {str(number): [{"kind": "ends", "hold": "run"}]})


def tools_run(stand_in: str) -> list[str]:
    """The tools that Claude Code's one run allows, once it starts."""
    overnight_files.until(lambda: len(claude_double.calls(stand_in)) == 1, what="the run")
    return claude_double.calls(stand_in)[0]["tools"]


@pytest.mark.supports(
    "test_the_walkthroughs_three_pieces_go_on_through_the_limit_and_show_done_in_a_later_session"
)
def test_the_walkthroughs_piece_is_handed_over_with_the_readmes_lines(repo: str, stand_in: str):
    """Given the walkthrough's repository
    When handover.py runs from its root with the walkthrough's tools and its prompt for #12
    Then it gives 0 with the README's four lines of piece 1, and Claude Code runs with the five
    tools"""
    held(stand_in)
    assert main([TOOLS_LINE], PROMPT, repo) == (0, handover_lines(1), "")
    assert tools_run(stand_in) == list(TOOLS)


@pytest.mark.supports(
    "test_a_piece_runs_with_the_named_tools_in_a_worktree_of_its_own_made_before_it_starts"
)
@pytest.mark.parametrize(
    ("written", "expected"),
    [
        ("Read", ["Read"]),
        ("Read,Edit,Bash(pytest:*)", ["Read", "Edit", "Bash(pytest:*)"]),
        ("Read, Bash(git commit -m *)", ["Read", "Bash(git commit -m *)"]),
    ],
    ids=["one tool", "commas with no spaces", "a rule that holds spaces"],
)
def test_each_tool_as_the_user_wrote_it_is_the_runs_and_no_other(
    repo: str, stand_in: str, written: str, expected: list[str]
):
    """Given the walkthrough's repository
    When handover.py runs with one tool, with tools apart by commas and no spaces, or with a rule
    that holds spaces inside its parentheses
    Then it gives 0, and Claude Code's run allows exactly those tools, each rule whole"""
    held(stand_in)
    code, _, err = main([written], PROMPT, repo)
    assert (code, err) == (0, "")
    assert tools_run(stand_in) == expected


@pytest.mark.supports(
    "test_a_new_piece_takes_the_number_after_the_highest_of_records_branches_and_worktrees"
)
def test_a_piece_of_two_digits_is_named_by_its_number_in_each_line(repo: str, stand_in: str):
    """Given the repository with the branch `overnight/9`
    When handover.py runs with the walkthrough's tools and prompt
    Then it gives 0 with the README's lines of piece 10"""
    git(repo, "branch", "overnight/9")
    held(stand_in, 10)
    assert main([TOOLS_LINE], PROMPT, repo) == (0, handover_lines(10), "")


@pytest.mark.supports("test_a_hand_over_with_no_prompt_is_refused_saying_what_to_add")
def test_a_hand_over_with_no_prompt_is_refused_saying_to_add_it(repo: str, stand_in: str):
    """Given the walkthrough's repository
    When handover.py runs with the walkthrough's tools and an empty standard input
    Then it gives 2, printing nothing, with words that name the prompt; no folder of a piece is
    made, no record is written, and Claude Code never runs"""
    code, out, err = main([TOOLS_LINE], "", repo)
    assert (code, out) == (2, "")
    assert "prompt" in err
    assert not os.path.exists(overnight_files.piece_folder(repo, 1))
    assert not os.path.exists(os.path.join(repo, ".overnight"))
    assert claude_double.calls(stand_in) == []


@pytest.mark.supports("test_a_hand_over_with_no_tool_named_is_refused_saying_what_to_add")
@pytest.mark.parametrize("argv", [[], [""], [", ,"]], ids=["no argument", "blank", "only commas"])
def test_a_hand_over_with_no_tool_named_is_refused_saying_to_add_one(
    repo: str, stand_in: str, argv: list[str]
):
    """Given the walkthrough's repository
    When handover.py runs with the walkthrough's prompt, and no argument, a blank one, or one of
    commas alone
    Then it gives 2, printing nothing, with words that name the tools; no folder of a piece is
    made, no record is written, and Claude Code never runs"""
    code, out, err = main(argv, PROMPT, repo)
    assert (code, out) == (2, "")
    assert "tool" in err.lower()
    assert not os.path.exists(overnight_files.piece_folder(repo, 1))
    assert not os.path.exists(os.path.join(repo, ".overnight"))
    assert claude_double.calls(stand_in) == []


@pytest.mark.supports("test_a_hand_over_outside_a_git_repository_is_refused_with_gits_words")
def test_a_hand_over_outside_a_git_repository_is_refused_with_gits_words(
    tmp_path: Any, stand_in: str
):
    """Given a folder that no Git repository holds
    When handover.py runs there with the walkthrough's tools and prompt
    Then it gives 2, printing nothing, with git's words that it isn't a repository, and Claude
    Code never runs"""
    outside = os.path.join(str(tmp_path), "outside")
    os.makedirs(outside)
    code, out, err = main([TOOLS_LINE], PROMPT, outside)
    assert (code, out) == (2, "")
    assert "not a git repository" in err.lower()
    assert claude_double.calls(stand_in) == []


@pytest.mark.supports("test_a_hand_over_in_a_repository_with_no_commit_is_refused_with_gits_words")
def test_a_hand_over_in_a_repository_with_no_commit_is_refused_with_gits_words(
    tmp_path: Any, stand_in: str
):
    """Given a repository made with `git init` and no commit yet
    When handover.py runs from its root with the walkthrough's tools and prompt
    Then it gives 2, printing nothing, with git's words; no record is written, and Claude Code
    never runs"""
    repo = overnight_files.repository(os.path.join(str(tmp_path), "work"), commit=False)
    code, out, err = main([TOOLS_LINE], PROMPT, repo)
    assert (code, out) == (2, "")
    assert err.strip()
    assert not os.path.exists(os.path.join(repo, ".overnight"))
    assert claude_double.calls(stand_in) == []
