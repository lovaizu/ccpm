"""The integration cases of S1, a piece handed over and carried to its end: the walkthrough's night,
each refusal of a hand-over, a repository with no commit yet among them, each way a piece's
conversation ends, each stop of the usage limit, the number a new piece takes, pieces run at once,
the prompt handed on whole, and where the records lie, each as ask and the runner run overnight's
scripts."""

from __future__ import annotations

import dataclasses
import os
from datetime import date, datetime

import overnight_files
import pytest
from claude_code import claude_double
from overnight_bench import Bench, stopped_at_night
from overnight_files import (
    LAST_WORDS,
    PROMPT,
    PROMPT_AS_OPTIONS,
    TOOLS_LINE,
    WALKTHROUGH_TABLE,
    git,
    handover_lines,
)

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's bodies aren't built yet")

PROMPT_15 = (
    "Fix issue #15: the CSV export drops its header row. Make tests/test_export.py::test_header"
    " pass, and change no other test. Run pytest to check, then commit on this branch.\n"
)
PROMPT_18 = (
    "Fix issue #18: add a --dry-run flag that prints each change and writes none. Add"
    " tests/test_cli.py::test_dry_run, run pytest to check, then commit on this branch.\n"
)


@pytest.mark.supports("S1", "S2", "ask", "status", "Piece")
def test_the_walkthroughs_three_pieces_go_on_through_the_limit_and_show_done_in_a_later_session(
    b: Bench,
):
    """Given the walkthrough's repository at 23:00, and Claude Code ending #12's piece at once,
    and stopping #15's and #18's at 01:12 by the session limit, which resets at 4:00am, before
    each ends with its last words
    When ask hands the three pieces over one by one, and status runs once each runner has ended
    Then handover.py gives the README's lines for each piece, and pieces.py the README's table:
    each piece done on its branch with its last words, the two stopped waited from 01:12 to 04:00,
    and 0 of 3 pieces stopped"""
    b.plays(
        {
            "1": [{"kind": "ends", "last_words": LAST_WORDS[0]}],
            "2": stopped_at_night(LAST_WORDS[1]),
            "3": stopped_at_night(LAST_WORDS[2], hold="third"),
        }
    )
    given = [b.hand(prompt) for prompt in (PROMPT, PROMPT_15, PROMPT_18)]
    b.until(lambda: len(b.calls(2)) == 2, what="piece 2 to go on after the reset")
    b.release("third")
    b.settle(3)
    assert given == [(0, handover_lines(n), "") for n in (1, 2, 3)]
    assert b.status() == (
        0,
        WALKTHROUGH_TABLE,
        "",
    )


@pytest.mark.supports("S1", "hand-over")
def test_a_hand_over_with_no_prompt_is_refused_saying_what_to_add(b: Bench):
    """Given the walkthrough's repository
    When ask hands a piece over with the walkthrough's tools and an empty prompt
    Then handover.py gives 2, printing nothing, with words that name the prompt to add; no
    piece's folder is made, Claude Code never runs, and status shows no pieces yet"""
    refused = b.hand(prompt="")
    assert (refused.code, refused.out) == (2, "")
    assert "prompt" in refused.err
    assert not os.path.exists(b.piece_folder(1))
    assert b.calls() == []
    assert b.status() == (0, "No pieces yet\n", "")


@pytest.mark.supports("S1", "hand-over")
def test_a_hand_over_with_no_tool_named_is_refused_saying_what_to_add(b: Bench):
    """Given the walkthrough's repository
    When ask hands the walkthrough's prompt over with no tool named
    Then handover.py gives 2, printing nothing, with words that name the tools to add; no
    piece's folder is made, Claude Code never runs, and status shows no pieces yet"""
    refused = b.hand(tools="")
    assert (refused.code, refused.out) == (2, "")
    assert "tool" in refused.err.lower()
    assert not os.path.exists(b.piece_folder(1))
    assert b.calls() == []
    assert b.status() == (0, "No pieces yet\n", "")


@pytest.mark.supports("hand-over", "Worktree")
def test_a_hand_over_outside_a_git_repository_is_refused_with_gits_words(b: Bench, tmp_path):
    """Given a folder that no Git repository holds
    When ask hands the walkthrough's piece over from it
    Then handover.py gives 2, printing nothing, with git's words that it isn't a repository,
    and Claude Code never runs"""
    outside = os.path.join(str(tmp_path), "outside")
    os.makedirs(outside)
    refused = b.script("handover", TOOLS_LINE, stdin=PROMPT, cwd=outside)
    assert (refused.code, refused.out) == (2, "")
    assert "not a git repository" in refused.err.lower()
    assert b.calls() == []


@pytest.mark.supports("hand-over", "Worktree")
def test_a_hand_over_in_a_repository_with_no_commit_is_refused_with_gits_words(b: Bench, tmp_path):
    """Given a repository made with `git init`, with no commit yet
    When ask hands the walkthrough's piece over from its root
    Then handover.py gives 2, printing nothing, with git's words; no record is written, Claude
    Code never runs, and status there shows no pieces yet"""
    fresh = overnight_files.repository(os.path.join(str(tmp_path), "fresh"), commit=False)
    refused = b.script("handover", TOOLS_LINE, stdin=PROMPT, cwd=fresh)
    assert (refused.code, refused.out) == (2, "")
    assert refused.err.strip()
    assert not os.path.exists(os.path.join(fresh, ".overnight"))
    assert b.calls() == []
    assert b.script("pieces", "report", cwd=fresh) == (0, "No pieces yet\n", "")


@pytest.mark.supports("S1", "runner", "Record")
def test_a_piece_ended_by_an_error_of_its_own_is_recorded_failed_with_the_error(b: Bench):
    """Given Claude Code ending the piece's run by an error of its own, its turns run out
    When ask hands the walkthrough's piece over, and its runner has ended
    Then status shows piece 1 failed on overnight/1, with no wait, and Claude Code's words of the
    error as its last words"""
    b.plays({"1": [{"kind": "errs"}]})
    b.hand()
    assert b.settle(1) == [
        {
            "Piece": "1",
            "State": "failed",
            "Branch": "overnight/1",
            "Waited": "-",
            "Last words": "Reached maximum number of turns (1)",
        }
    ]


def without_claude(b: Bench) -> Bench:
    """The bench with a PATH that holds git and Python but no `claude`, where the machine allows
    one."""
    return dataclasses.replace(b, env={**b.env, "PATH": overnight_files.path_without_claude()})


@pytest.mark.supports("S1", "runner")
def test_a_piece_whose_claude_code_cant_start_is_recorded_failed_with_the_systems_words(b: Bench):
    """Given a PATH on which no `claude` is found
    When ask hands the walkthrough's piece over
    Then handover.py gives the piece's lines, and status shows piece 1 failed on overnight/1,
    with no wait, and the system's words of `claude` not found as its last words"""
    alone = without_claude(b)
    assert alone.hand() == (0, handover_lines(1), "")
    b.until(lambda: [row["State"] for row in alone.rows()] == ["failed"], what="piece 1 to fail")
    (row,) = alone.rows()
    assert (row["Piece"], row["Branch"], row["Waited"]) == ("1", "overnight/1", "-")
    assert row["Last words"]


@pytest.mark.supports("S1", "hand-over", "Worktree")
def test_a_new_piece_takes_the_number_after_the_highest_of_records_branches_and_worktrees(
    b: Bench,
):
    """Given a repository whose one record, of an earlier day, holds piece 9, with a branch
    overnight/5 and a folder ../myapp-overnight-7 beside it
    When ask hands the walkthrough's piece over
    Then handover.py gives piece 10, in ../myapp-overnight-10 on overnight/10, and Claude Code
    runs there"""
    b.plays({"1": [{"kind": "ends"}], "10": [{"kind": "ends"}]})
    b.hand()
    b.settle(1)
    (record,) = os.listdir(b.at(".overnight"))
    os.rename(b.at(f".overnight/{record}"), b.at(".overnight/20261120-9"))
    git(b.repo, "branch", "overnight/5")
    os.makedirs(b.piece_folder(7))
    assert b.hand() == (0, handover_lines(10), "")
    b.settle(2)
    assert [each["cwd"] for each in b.calls(10)] == [os.path.realpath(b.piece_folder(10))]


@pytest.mark.supports("S1", "runner")
def test_each_piece_starts_at_its_hand_over_while_the_others_run(b: Bench):
    """Given Claude Code holding each piece's run until the case releases it
    When ask hands three pieces over one after another
    Then Claude Code runs for each of the three before any is released, status shows the three
    running, and once released each is done"""
    held = [{"kind": "ends", "hold": "night", "last_words": "Done."}]
    b.plays({"1": held, "2": held, "3": held})
    for prompt in (PROMPT, PROMPT_15, PROMPT_18):
        b.hand(prompt)
    b.until(lambda: len(b.calls()) == 3, what="a run of each of the three pieces")
    assert [row["State"] for row in b.rows()] == ["running", "running", "running"]
    b.release("night")
    assert [row["State"] for row in b.settle(3)] == ["done", "done", "done"]


@pytest.mark.supports("S1", "Piece")
def test_the_prompt_reaches_claude_code_whole_on_its_standard_input(b: Bench):
    """Given a prompt of several lines that starts with an option of Claude Code's and holds
    quotes, a line `Tools:`, and words beyond ASCII
    When ask hands it over with the walkthrough's tools
    Then Claude Code's one run takes the prompt on its standard input as written"""
    b.plays({"1": [{"kind": "ends"}]})
    b.hand(PROMPT_AS_OPTIONS)
    b.settle(1)
    assert [each["stdin"] for each in b.calls(1)] == [PROMPT_AS_OPTIONS]


@pytest.mark.supports("Wait", "runner")
def test_a_limit_that_gives_no_reset_time_is_waited_a_set_while_and_the_piece_goes_on(b: Bench):
    """Given Claude Code stopping the piece at 23:00 by a usage limit whose words give no reset
    time, and then ending it
    When ask hands the walkthrough's piece over, and its runner has ended
    Then the runner waited once, from 23:00 until a later time, went on in the same
    conversation, and status shows piece 1 done with its wait from 23:00"""
    b.plays({"1": [{"kind": "limit with no time"}, {"kind": "ends", "last_words": "Done."}]})
    b.hand()
    (row,) = b.settle(1)
    (waited,) = b.waits()
    assert datetime.fromisoformat(waited["until"]) > datetime.fromisoformat(waited["from"])
    conversation = claude_double.conversation(b.piece_folder(1))
    assert [each["resume"] for each in b.calls(1)] == [None, conversation]
    assert (row["Piece"], row["State"], row["Last words"]) == ("1", "done", "Done.")
    assert row["Waited"].startswith("usage limit, 23:00 to ")


@pytest.mark.supports("Wait", "Conversation")
def test_a_weekly_limit_is_waited_until_its_day_and_time(b: Bench):
    """Given the bench's clock at 23:00 of Tuesday 2026-11-24, and Claude Code stopping the piece
    by the weekly limit, which resets on Mon 12:00am, and then ending it
    When ask hands the walkthrough's piece over, and its runner has ended
    Then the runner waited once, from 23:00 of the Tuesday until 00:00 of Monday 2026-11-30, and
    status shows piece 1 done"""
    b.plays({"1": [{"kind": "weekly limit"}, {"kind": "ends", "last_words": "Done."}]})
    b.hand()
    (row,) = b.settle(1)
    (waited,) = b.waits()
    assert datetime.fromisoformat(waited["from"]) == datetime(2026, 11, 24, 23, 0).astimezone()
    assert datetime.fromisoformat(waited["until"]) == datetime(2026, 11, 30, 0, 0).astimezone()
    assert (row["State"], row["Last words"]) == ("done", "Done.")


@pytest.mark.supports("Record", "pieces")
def test_the_records_lie_in_overnight_at_the_root_and_one_gitignore_line_keeps_them_out(b: Bench):
    """Given the walkthrough's repository, whose `.gitignore` holds the one line `.overnight/`
    When ask hands the walkthrough's piece over, and its runner has ended
    Then `.overnight/` at the repository's root holds the one folder `<yyyymmdd>-1` of today,
    and git sees the person's folder as it was"""
    b.plays({"1": [{"kind": "ends"}]})
    b.hand()
    b.settle(1)
    assert os.listdir(b.at(".overnight")) == [f"{date.today():%Y%m%d}-1"]
    assert git(b.repo, "status", "--porcelain") == ""
