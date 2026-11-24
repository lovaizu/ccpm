"""The integration cases of each principle item of overnight's architecture: each where the scripts
keep it, as ask, the runner, and status run them, and each with the fixture `broken`, which takes
the part that holds the item out of the bench's copy of overnight where TRACE_BROKEN is 1."""

from __future__ import annotations

import os
import time

import overnight_bench
import overnight_files
import pytest
from claude_code import claude_double
from overnight_bench import Bench
from overnight_files import LAST_WORDS, SHARE, TOOLS, git

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's bodies aren't built yet")

# P1: waiting out the usage limit.


@pytest.mark.supports("P1.1", "Conversation", "Wait")
def test_a_piece_the_limit_stops_twice_goes_on_in_its_conversation_after_each_reset(
    b: Bench, broken: None
):
    """Given Claude Code stopping the piece at 23:00 by the session limit, which resets at
    11:30pm, and again at 23:30, which resets at 11:50pm, before it ends with its last words
    When ask hands the walkthrough's piece over, and its runner has ended
    Then Claude Code ran three times in the piece's folder, first anew and then twice in the
    conversation that its first reply named; the runner waited until 23:30 and until 23:50; and
    status shows piece 1 done with its last words"""
    b.plays(
        {
            "1": [
                {"kind": "session limit", "resets": "11:30pm"},
                {"kind": "session limit", "resets": "11:50pm"},
                {"kind": "ends", "last_words": LAST_WORDS[0]},
            ]
        }
    )
    b.hand()
    (row,) = b.settle(1)
    conversation = claude_double.conversation(b.piece_folder(1))
    assert [each["resume"] for each in b.calls(1)] == [None, conversation, conversation]
    assert [each["until"][11:16] for each in b.waits()] == ["23:30", "23:50"]
    assert (row["State"], row["Last words"]) == ("done", LAST_WORDS[0])


# P2: nothing to answer.


@pytest.mark.supports("P2.1", "Worktree")
def test_a_piece_runs_with_the_named_tools_in_a_worktree_of_its_own_made_before_it_starts(
    b: Bench, broken: None
):
    """Given the walkthrough's repository on its branch main
    When ask hands the walkthrough's piece over with its five tools
    Then Claude Code's one run allows exactly those tools, in ../myapp-overnight-1, a worktree of
    the repository on the branch overnight/1"""
    b.plays({"1": [{"kind": "ends"}]})
    b.hand()
    b.settle(1)
    (run,) = b.calls()
    folder = b.piece_folder(1)
    assert (run["cwd"], run["tools"]) == (os.path.realpath(folder), list(TOOLS))
    assert git(folder, "branch", "--show-current") == "overnight/1\n"
    assert os.path.realpath(folder) in git(b.repo, "worktree", "list")


@pytest.mark.supports("P2.2")
def test_a_call_to_a_tool_not_named_is_refused_at_once_and_the_piece_goes_on_to_its_end(
    b: Bench, broken: None
):
    """Given a piece whose run calls `touch made.txt` by Bash, a tool the user didn't name
    When ask hands it over with the walkthrough's tools, none of which allows the call
    Then Claude Code runs in its mode that asks no one, the call is refused and never made, and
    status shows piece 1 done with its last words"""
    b.plays({"1": [{"kind": "refuses", "last_words": "Refused."}]})
    b.hand()
    (row,) = b.settle(1)
    (run,) = b.calls()
    assert run["mode"] == "dontAsk"
    assert not os.path.exists(os.path.join(b.piece_folder(1), "made.txt"))
    assert (row["State"], row["Last words"]) == ("done", "Refused.")


# P3: running past the session.


@pytest.mark.supports("P3.1", "runner")
def test_a_piece_goes_on_after_the_session_that_handed_it_over_closes(b: Bench, broken: None):
    """Given a piece whose run Claude Code holds until the case releases it
    When ask hands it over from a session of its own, the session closes while the run is held,
    and the case then releases it
    Then handover.py gave 0 while the piece ran, and status shows piece 1 done with its last
    words"""
    b.plays({"1": [{"kind": "ends", "hold": "closing", "last_words": LAST_WORDS[0]}]})
    given, group = overnight_bench.session(b)
    b.until(lambda: len(b.calls()) == 1, what="the piece's run")
    overnight_bench.close_session(group)
    b.release("closing")
    (row,) = b.settle(1)
    assert given.code == 0
    assert (row["State"], row["Last words"]) == ("done", LAST_WORDS[0])


@pytest.mark.supports("P3.2", "Record")
def test_a_record_read_while_its_runner_writes_it_is_read_whole_each_time(b: Bench, broken: None):
    """Given a piece that the session limit stops three times before it ends
    When status runs again and again from another session while the runner records each wait
    and each run again
    Then each status gives 0, and the last shows piece 1 done with its three waits"""
    stop = {"kind": "session limit", "resets": "11:01pm"}
    b.plays({"1": [stop, stop, stop, {"kind": "ends", "last_words": "Done."}]})
    b.hand()
    codes = []
    end = time.monotonic() + 30
    while time.monotonic() < end and (
        not b.runners() or any(map(overnight_files.alive, b.runners()))
    ):
        codes.append(b.status().code)
    (row,) = b.settle(1)
    assert set(codes) <= {0}
    assert (row["State"], row["Last words"]) == ("done", "Done.")
    assert len(b.waits()) == 3


# P4: no more than the user let it.


@pytest.mark.supports("P4.1", "Worktree")
def test_a_pieces_changes_stay_on_its_branch_and_the_persons_branch_and_folder_as_they_were(
    b: Bench, broken: None
):
    """Given the walkthrough's repository on main, and a piece whose run commits fix.txt
    When ask hands it over, and its runner has ended
    Then overnight/1 holds the commit, while main stays at its commit, the person's folder stays
    on main without fix.txt, and git sees it as it was"""
    head = git(b.repo, "rev-parse", "main")
    b.plays({"1": [{"kind": "ends", "commit": "fix.txt"}]})
    b.hand()
    b.settle(1)
    assert git(b.repo, "log", "-1", "--format=%s", "overnight/1") == "Fix by fix.txt\n"
    assert git(b.repo, "rev-parse", "main") == head
    assert git(b.repo, "branch", "--show-current") == "main\n"
    assert not os.path.exists(b.at("fix.txt"))
    assert git(b.repo, "status", "--porcelain") == ""


# P5: how the night went, seen at a glance.


@pytest.mark.supports("P5.1", "Wait", "Record")
def test_a_pieces_wait_is_shown_while_it_waits_and_its_last_words_once_it_ends(
    b: Bench, broken: None
):
    """Given a piece that the session limit stops at 01:12, which resets at 4:00am, before it ends
    with its last words, and the runner's wait held while the case looks
    When status runs while the piece waits, and again once its runner has ended
    Then the first shows piece 1 waiting on overnight/1 with its wait from 01:12 to 04:00, and
    the last shows it done with the same wait and its last words"""
    b.plays(
        {
            "1": [
                {"kind": "session limit", "at": "2026-11-25T01:12:00", "resets": "4:00am"},
                {"kind": "ends", "last_words": LAST_WORDS[1]},
            ]
        }
    )
    b.hold_waits()
    b.hand()
    b.until(lambda: b.rows()[0]["State"] == "waiting", timeout=10, what="piece 1 to wait")
    (waiting,) = b.rows()
    b.release_waits()
    (row,) = b.settle(1)
    shown = ("Piece", "State", "Branch", "Waited")
    assert [waiting[each] for each in shown] == [
        "1",
        "waiting",
        "overnight/1",
        "usage limit, 01:12 to 04:00",
    ]
    assert row == {
        "Piece": "1",
        "State": "done",
        "Branch": "overnight/1",
        "Waited": "usage limit, 01:12 to 04:00",
        "Last words": LAST_WORDS[1],
    }


@pytest.mark.supports("P5.2", "pieces")
def test_a_piece_whose_runner_ended_while_it_ran_is_shown_stopped_by_the_session_closing(
    b: Bench, broken: None
):
    """Given piece 1 whose run Claude Code holds, and piece 2 done
    When piece 1's runner and its run end, as the OS shuts them down, and status runs
    Then status shows piece 1 no longer running, with the session closing as what stopped it,
    and 1 of 2 pieces stopped"""
    b.plays(
        {"1": [{"kind": "ends", "hold": "run"}], "2": [{"kind": "ends", "last_words": "Done."}]}
    )
    b.hand()
    b.until(lambda: len(b.calls(1)) == 1, what="piece 1's run")
    (run,) = b.calls(1)
    overnight_files.kill(run["ppid"])
    overnight_files.kill(run["pid"])
    b.hand()
    first, second = b.settle(2)
    shown = b.status().out.splitlines()
    assert first["State"] != "running"
    assert "session closing" in shown[1]
    assert second["State"] == "done"
    assert shown[-1] == SHARE.format(1, 2)


@pytest.mark.supports("P5.3", "status")
def test_the_share_stopped_counts_neither_a_failed_piece_nor_one_with_a_refused_call(
    b: Bench, broken: None
):
    """Given piece 1 done after a call refused on the way, piece 2 failed by an error of its own,
    and piece 3 whose runner ends while it runs, as the OS shuts it down
    When status runs once each runner has ended
    Then its last line says 1 of 3 pieces stopped"""
    b.plays(
        {
            "1": [{"kind": "refuses", "last_words": "Refused."}],
            "2": [{"kind": "errs"}],
            "3": [{"kind": "ends", "hold": "run"}],
        }
    )
    for _ in range(3):
        b.hand()
    b.until(lambda: len(b.calls(3)) == 1, what="piece 3's run")
    (run,) = b.calls(3)
    overnight_files.kill(run["ppid"])
    overnight_files.kill(run["pid"])
    b.settle(3)
    assert b.status().out.splitlines()[-1] == SHARE.format(1, 3)
