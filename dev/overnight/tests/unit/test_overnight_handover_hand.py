"""The unit cases of handover/hand.py, the order in which a piece is set up and started:
`hand_over`, of the first piece and of one beside a piece that runs, each recorded as running with
the process that carries it; and of a repository where git can't make the worktree."""

from __future__ import annotations

import os
from typing import Any

import overnight_files
import pytest
from claude_code import claude_double
from handover.hand import hand_over
from handover.worktree import Refused
from overnight_files import PROMPT, TOOLS
from pieces.record import read

pytestmark = pytest.mark.xfail(strict=True, reason="handover.hand isn't built yet")

PROMPT_15 = "Fix issue #15: the CSV export drops its header row.\n"


def held_run(number: int) -> dict[str, Any]:
    """The play of a run of the piece that Claude Code holds until the case releases it."""
    return {"kind": "ends", "hold": f"run-{number}", "last_words": "Done."}


@pytest.mark.supports(
    "test_the_walkthroughs_three_pieces_go_on_through_the_limit_and_show_done_in_a_later_session"
)
def test_the_first_piece_is_set_up_started_and_recorded_running_with_its_runner(
    repo: str, stand_in: str
):
    """Given the walkthrough's repository, and Claude Code holding the piece's run
    When the walkthrough's piece is handed over with its five tools
    Then it gives piece 1, in `../myapp-overnight-1` on `overnight/1`, with the five tools; Claude
    Code runs there with the prompt; and the one record is running, with no wait and no last
    words, carried by the parent of that run"""
    claude_double.plays(stand_in, {"1": [held_run(1)]})
    handed = hand_over(repo, PROMPT, TOOLS)
    folder = overnight_files.piece_folder(repo, 1)
    assert (handed.number, handed.branch, handed.tools) == (1, "overnight/1", TOOLS)
    assert os.path.realpath(os.path.join(repo, handed.folder)) == os.path.realpath(folder)
    overnight_files.until(lambda: len(claude_double.calls(stand_in)) == 1, what="the run")
    (call,) = claude_double.calls(stand_in)
    assert (call["cwd"], call["stdin"]) == (os.path.realpath(folder), PROMPT)
    (record,) = read(repo)
    assert (record.handed, record.state, record.waits, record.last_words) == (
        handed,
        "running",
        (),
        "",
    )
    assert record.runner.pid == call["ppid"]


@pytest.mark.supports("test_each_piece_starts_at_its_hand_over_while_the_others_run")
def test_a_piece_handed_over_while_one_runs_takes_the_next_number_and_starts_at_once(
    repo: str, stand_in: str
):
    """Given piece 1 handed over, whose run Claude Code holds
    When a second piece is handed over with the one tool `Read`
    Then it gives piece 2 on `overnight/2` with that tool; Claude Code runs for both while the
    first is held; and the records are of 1 and 2, each running, with runners of their own"""
    claude_double.plays(stand_in, {"1": [held_run(1)], "2": [held_run(2)]})
    hand_over(repo, PROMPT, TOOLS)
    second = hand_over(repo, PROMPT_15, ("Read",))
    assert (second.number, second.branch, second.tools) == (2, "overnight/2", ("Read",))
    overnight_files.until(lambda: len(claude_double.calls(stand_in)) == 2, what="both runs")
    records = read(repo)
    assert [(each.handed.number, each.state) for each in records] == [
        (1, "running"),
        (2, "running"),
    ]
    assert records[0].runner != records[1].runner


@pytest.mark.supports("test_a_hand_over_in_a_repository_with_no_commit_is_refused_with_gits_words")
def test_a_hand_over_where_git_cant_make_the_worktree_is_refused_and_starts_nothing(
    tmp_path: Any, stand_in: str
):
    """Given a repository made with `git init` and no commit yet
    When the walkthrough's piece is handed over
    Then Refused is raised with git's words; no record is read, and Claude Code never runs"""
    repo = overnight_files.repository(os.path.join(str(tmp_path), "work"), commit=False)
    with pytest.raises(Refused) as refused:
        hand_over(repo, PROMPT, TOOLS)
    assert str(refused.value).strip()
    assert read(repo) == []
    assert claude_double.calls(stand_in) == []
