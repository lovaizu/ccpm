"""The unit cases of pieces/command.py, pieces.py's command line: `report` of no piece, of the
walkthrough's night, of a piece failed, of one running, of pieces stopped among others, and of a
record out of its layout; and each set of arguments other than `report`."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime

import pytest
from overnight_bench import rows_of
from overnight_files import LAST_WORDS, SHARE
from pieces.command import main
from pieces.record import Handed, begin, end, resume, wait

pytestmark = pytest.mark.xfail(strict=True, reason="pieces.command isn't built yet")

# The walkthrough's wait, in the zone of the machine, as status shows each time in it.
STOP = datetime(2026, 11, 25, 1, 12).astimezone()
RESET = datetime(2026, 11, 25, 4, 0).astimezone()
WAITED = "usage limit, 01:12 to 04:00"


def table(rows: list[tuple[str, str, str, str, str]], stopped: int) -> str:
    """The table that status shows of the rows, in the README's form: each column as wide as its
    widest cell and two spaces more, the last as its cells are, then a blank line and the share
    line."""
    lines = [("Piece", "State", "Branch", "Waited", "Last words"), *rows]
    widths = [max(len(line[at]) for line in lines) + 2 for at in range(4)]
    shown = ["".join(c.ljust(w) for c, w in zip(line, widths)) + line[4] for line in lines]
    return "\n".join([*shown, "", SHARE.format(stopped, len(rows))]) + "\n"


def recorded(repo: str, number: int, pid: int | None = None) -> None:
    """Records the walkthrough's piece of the number as begun, carried by the process of the ID,
    this one where none is given."""
    piece = Handed(number, f"../myapp-overnight-{number}", f"overnight/{number}", ("Read",))
    begin(repo, piece, pid or os.getpid())


def runner_ended() -> subprocess.Popen:
    """A child process that runs until the case ends it."""
    return subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])


def ends(child: subprocess.Popen) -> None:
    child.kill()
    child.wait()


@pytest.mark.supports("test_status_with_no_piece_handed_over_shows_no_pieces_yet")
def test_report_of_no_piece_shows_no_pieces_yet(repo: str):
    """Given the walkthrough's repository, with no record
    When pieces.py report runs from its root
    Then it gives 0 with `No pieces yet`"""
    assert main(["report"], repo) == (0, "No pieces yet\n", "")


@pytest.mark.supports(
    "test_the_walkthroughs_three_pieces_go_on_through_the_limit_and_show_done_in_a_later_session"
)
def test_report_of_the_walkthroughs_night_shows_the_readmes_table(repo: str):
    """Given piece 1 done with its last words, and pieces 2 and 3 each done after a wait from
    01:12 to 04:00, with their last words, as the README's walkthrough gives them
    When pieces.py report runs from the repository's root
    Then it gives 0 with the README's table, and 0 of 3 pieces stopped"""
    for number in (1, 2, 3):
        recorded(repo, number)
    end(repo, 1, "done", LAST_WORDS[0])
    for number in (2, 3):
        wait(repo, number, STOP, RESET)
        resume(repo, number)
        end(repo, number, "done", LAST_WORDS[number - 1])
    shown = main(["report"], repo)
    assert shown == (
        0,
        (
            "Piece  State  Branch       Waited                       Last words\n"
            f"1      done   overnight/1  -                            {LAST_WORDS[0]}\n"
            f"2      done   overnight/2  usage limit, 01:12 to 04:00  {LAST_WORDS[1]}\n"
            f"3      done   overnight/3  usage limit, 01:12 to 04:00  {LAST_WORDS[2]}\n"
            "\n"
            f"{SHARE.format(0, 3)}\n"
        ),
        "",
    )
    assert shown[1] == table(
        [
            ("1", "done", "overnight/1", "-", LAST_WORDS[0]),
            ("2", "done", "overnight/2", WAITED, LAST_WORDS[1]),
            ("3", "done", "overnight/3", WAITED, LAST_WORDS[2]),
        ],
        0,
    )


@pytest.mark.supports(
    "test_a_piece_ended_by_an_error_of_its_own_is_recorded_failed_with_the_error"
)
def test_report_of_a_piece_failed_and_one_done_shows_the_error_as_last_words_and_none_stopped(
    repo: str,
):
    """Given piece 1 failed with Claude Code's words of its error, and piece 2 done
    When pieces.py report runs
    Then it gives 0 with piece 1 failed, its error as its last words, and 0 of 2 stopped"""
    recorded(repo, 1)
    recorded(repo, 2)
    end(repo, 1, "failed", "Reached maximum number of turns (1)")
    end(repo, 2, "done", "Done.")
    assert main(["report"], repo) == (
        0,
        table(
            [
                ("1", "failed", "overnight/1", "-", "Reached maximum number of turns (1)"),
                ("2", "done", "overnight/2", "-", "Done."),
            ],
            0,
        ),
        "",
    )


@pytest.mark.supports("test_each_piece_starts_at_its_hand_over_while_the_others_run")
def test_report_of_pieces_running_and_waiting_whose_runners_run_shows_them_so(repo: str):
    """Given piece 1 running, and piece 2 waiting from 01:12 to 04:00, each carried by this
    process, which runs
    When pieces.py report runs
    Then it gives 0 with piece 1 running with no wait, piece 2 waiting with its wait, and 0 of 2
    stopped"""
    recorded(repo, 1)
    recorded(repo, 2)
    wait(repo, 2, STOP, RESET)
    code, out, err = main(["report"], repo)
    assert (code, err) == (0, "")
    shown = [[row[name] for name in ("Piece", "State", "Branch", "Waited")] for row in rows_of(out)]
    assert shown == [["1", "running", "overnight/1", "-"], ["2", "waiting", "overnight/2", WAITED]]
    assert out.splitlines()[-1] == SHARE.format(0, 2)


@pytest.mark.supports(
    "test_a_piece_whose_runner_ended_while_it_ran_is_shown_stopped_by_the_session_closing"
)
def test_report_of_pieces_whose_runners_ended_names_what_stopped_each_and_counts_them(repo: str):
    """Given piece 1 running and piece 2 waiting, whose runner then ended, and piece 3 done
    When pieces.py report runs
    Then it gives 0, with neither 1 shown running nor 2 waiting, 1's line naming the session
    closing and 2's the usage limit, and 2 of 3 pieces stopped"""
    child = runner_ended()
    recorded(repo, 1, child.pid)
    recorded(repo, 2, child.pid)
    recorded(repo, 3)
    wait(repo, 2, STOP, RESET)
    end(repo, 3, "done", "Done.")
    ends(child)
    code, out, err = main(["report"], repo)
    lines = out.splitlines()
    rows = rows_of(out)
    assert (code, err) == (0, "")
    assert rows[0]["State"] != "running" and rows[1]["State"] != "waiting"
    assert "session closing" in lines[1]
    assert "usage limit" in lines[2].replace(WAITED, "")
    assert lines[-1] == SHARE.format(2, 3)


@pytest.mark.supports("test_a_record_left_out_of_its_layout_is_refused_naming_its_file")
def test_report_with_a_record_out_of_its_layout_is_refused_naming_its_file(repo: str):
    """Given the record of piece 1, which a person then overwrote with text that isn't JSON
    When pieces.py report runs
    Then it gives 2, printing nothing, with words that name the record's file"""
    recorded(repo, 1)
    (day,) = os.listdir(os.path.join(repo, ".overnight"))
    (name,) = os.listdir(os.path.join(repo, ".overnight", day))
    with open(os.path.join(repo, ".overnight", day, name), "w", encoding="utf-8") as f:
        f.write("{not json")
    code, out, err = main(["report"], repo)
    assert (code, out) == (2, "")
    assert name in err


@pytest.mark.supports("test_status_with_no_piece_handed_over_shows_no_pieces_yet")
@pytest.mark.parametrize(
    "argv", [[], ["status"], ["report", "extra"]], ids=["none", "another word", "one more"]
)
def test_arguments_other_than_report_are_refused_with_the_usage(repo: str, argv: list[str]):
    """Given the walkthrough's repository
    When pieces.py runs with no argument, with another word, or with `report` and one more
    Then it gives 2, printing nothing, with its usage"""
    code, out, err = main(argv, repo)
    assert (code, out) == (2, "")
    assert "usage: pieces.py report" in err
