"""The unit cases of pieces/record.py, each piece's record on disk: `highest`, of no `.overnight/`,
of none, one, and several pieces' folders, beside folders and files of other names; `begin`, of
one tool and several, of a number beside one that nearly matches, each refusal; `wait`, `resume`,
and `end`, each change from the state that the runner brings the record into, of one wait and
several, and each refusal; and `read`, of none, one, and several records in the order of their
numbers, and each record out of its layout."""

from __future__ import annotations

import os
from datetime import date, timedelta

import overnight_files
import pytest
from overnight_files import TOOLS, handed
from overnight_stand_ins import RESET, STOP
from pieces.process import identify
from pieces.record import Record, Wait, begin, end, highest, read, resume, wait

pytestmark = pytest.mark.xfail(strict=True, reason="pieces.record isn't built yet")


def folder(repo: str, number: int, day: str | None = None) -> str:
    """The folder of the record of the number, of today or of the day."""
    return os.path.join(repo, ".overnight", f"{day or f'{date.today():%Y%m%d}'}-{number}")


def running(number: int = 1, tools: tuple[str, ...] = TOOLS) -> Record:
    """The record that `begin` gives of the piece of the number, carried by this process."""
    return Record(handed(number, tools), "running", identify(os.getpid()), (), "")


# highest


@pytest.mark.supports(
    "test_a_new_piece_takes_the_number_after_the_highest_of_records_branches_and_worktrees"
)
def test_highest_of_a_repository_with_no_overnight_folder_is_0(repo: str):
    """Given a repository with no `.overnight/`
    When the highest number of its records is asked
    Then it is 0, and no `.overnight/` is made"""
    assert highest(repo) == 0
    assert not os.path.exists(os.path.join(repo, ".overnight"))


@pytest.mark.supports(
    "test_a_new_piece_takes_the_number_after_the_highest_of_records_branches_and_worktrees"
)
def test_highest_of_an_empty_overnight_folder_is_0(repo: str):
    """Given a repository whose `.overnight/` holds nothing
    When the highest number of its records is asked
    Then it is 0"""
    os.makedirs(os.path.join(repo, ".overnight"))
    assert highest(repo) == 0


@pytest.mark.supports(
    "test_a_new_piece_takes_the_number_after_the_highest_of_records_branches_and_worktrees"
)
def test_highest_of_one_pieces_folder_is_its_number(repo: str):
    """Given a repository whose `.overnight/` holds the one folder `20261124-3`
    When the highest number of its records is asked
    Then it is 3"""
    os.makedirs(folder(repo, 3, "20261124"))
    assert highest(repo) == 3


@pytest.mark.supports(
    "test_a_new_piece_takes_the_number_after_the_highest_of_records_branches_and_worktrees"
)
def test_highest_of_several_is_the_greatest_number_whatever_its_day_or_order(repo: str):
    """Given `.overnight/` with `20261120-12`, `20261124-3`, and `20261124-9`, whose greatest
    number is neither the latest day's, nor first or last by name
    When the highest number of its records is asked
    Then it is 12"""
    for number, day in ((12, "20261120"), (3, "20261124"), (9, "20261124")):
        os.makedirs(folder(repo, number, day))
    assert highest(repo) == 12


@pytest.mark.supports(
    "test_a_new_piece_takes_the_number_after_the_highest_of_records_branches_and_worktrees"
)
def test_highest_leaves_out_each_folder_and_file_that_isnt_a_pieces_folder(repo: str):
    """Given `.overnight/` with the folder `20261124-2`, beside folders `notes-99`,
    `20261124-`, `20261124-7x`, `x20261124-98`, and a file `20261124-50`
    When the highest number of its records is asked
    Then it is 2"""
    os.makedirs(folder(repo, 2, "20261124"))
    for name in ("notes-99", "20261124-", "20261124-7x", "x20261124-98"):
        os.makedirs(os.path.join(repo, ".overnight", name))
    with open(os.path.join(repo, ".overnight", "20261124-50"), "w", encoding="utf-8") as f:
        f.write("")
    assert highest(repo) == 2


# begin


@pytest.mark.supports(
    "test_the_walkthroughs_three_pieces_go_on_through_the_limit_and_show_done_in_a_later_session"
)
def test_begin_records_the_piece_running_with_its_runner_no_wait_and_no_last_words(repo: str):
    """Given a repository with no record, and the walkthrough's piece 1 with its five tools,
    carried by this process
    When it's recorded as begun
    Then the record is running, with this process as its runner, no wait, and no last words, in
    one file of `.overnight/<yyyymmdd>-1/` of today, and a read gives it"""
    given = begin(repo, handed(), os.getpid())
    assert given == running()
    assert len(os.listdir(folder(repo, 1))) == 1
    assert read(repo) == [running()]


@pytest.mark.supports(
    "test_a_piece_runs_with_the_named_tools_in_a_worktree_of_its_own_made_before_it_starts"
)
def test_begin_keeps_a_piece_of_one_tool(repo: str):
    """Given the piece 1 with the one tool `Read`
    When it's recorded as begun
    Then a read gives it with that one tool"""
    begin(repo, handed(tools=("Read",)), os.getpid())
    assert read(repo) == [running(tools=("Read",))]


@pytest.mark.supports(
    "test_a_new_piece_takes_the_number_after_the_highest_of_records_branches_and_worktrees"
)
def test_begin_of_1_beside_a_record_of_10_records_it(repo: str):
    """Given a repository with the record of piece 10, whose number starts as 1's does
    When piece 1 is recorded as begun
    Then both records are read, 1 first"""
    begin(repo, handed(10), os.getpid())
    begin(repo, handed(1), os.getpid())
    assert read(repo) == [running(1), running(10)]


@pytest.mark.supports(
    "test_a_new_piece_takes_the_number_after_the_highest_of_records_branches_and_worktrees"
)
def test_begin_of_a_number_recorded_today_is_refused(repo: str):
    """Given a repository with the record of piece 1, of today
    When piece 1 is recorded as begun again
    Then FileExistsError is raised, and the record stays as it was"""
    begin(repo, handed(), os.getpid())
    with pytest.raises(FileExistsError):
        begin(repo, handed(tools=("Read",)), os.getpid())
    assert read(repo) == [running()]


@pytest.mark.supports(
    "test_a_new_piece_takes_the_number_after_the_highest_of_records_branches_and_worktrees"
)
def test_begin_of_a_number_recorded_on_an_earlier_day_is_refused(repo: str):
    """Given a repository with the record of piece 1, of an earlier day
    When piece 1 is recorded as begun today
    Then FileExistsError is raised, and no folder of today is made"""
    begin(repo, handed(), os.getpid())
    os.rename(folder(repo, 1), folder(repo, 1, "20261120"))
    with pytest.raises(FileExistsError):
        begin(repo, handed(), os.getpid())
    assert not os.path.exists(folder(repo, 1))


@pytest.mark.supports(
    "test_a_piece_whose_claude_code_cant_start_is_recorded_failed_with_the_systems_words"
)
def test_begin_with_a_runner_that_no_longer_runs_is_refused(repo: str):
    """Given the ID of a process that ran and has ended
    When piece 1 is recorded as begun with it as its runner
    Then LookupError is raised, and no record is read"""
    with pytest.raises(LookupError):
        begin(repo, handed(), overnight_files.ended_process())
    assert read(repo) == []


# wait, resume, and end


@pytest.mark.supports("test_a_pieces_wait_is_shown_while_it_waits_and_its_last_words_once_it_ends")
def test_wait_of_a_running_piece_records_it_waiting_with_the_wait(repo: str):
    """Given piece 1 recorded running
    When its wait from 01:12 to 04:00 is recorded
    Then the record, as given and as read, is waiting with that one wait"""
    begin(repo, handed(), os.getpid())
    expected = Record(handed(), "waiting", identify(os.getpid()), (Wait(STOP, RESET),), "")
    assert wait(repo, 1, STOP, RESET) == expected
    assert read(repo) == [expected]


@pytest.mark.supports("test_a_pieces_wait_is_shown_while_it_waits_and_its_last_words_once_it_ends")
def test_resume_of_a_waiting_piece_records_it_running_with_its_wait_kept(repo: str):
    """Given piece 1 recorded waiting from 01:12 to 04:00
    When it's recorded as running again
    Then the record, as given and as read, is running with that wait"""
    begin(repo, handed(), os.getpid())
    wait(repo, 1, STOP, RESET)
    expected = Record(handed(), "running", identify(os.getpid()), (Wait(STOP, RESET),), "")
    assert resume(repo, 1) == expected
    assert read(repo) == [expected]


@pytest.mark.supports(
    "test_a_piece_the_limit_stops_twice_goes_on_in_its_conversation_after_each_reset"
)
def test_waits_of_several_stops_are_kept_in_order_the_latest_last(repo: str):
    """Given piece 1 that waited from 01:12 to 04:00 and ran again
    When its wait from 05:00 to 09:00 is recorded, and it runs again
    Then the record is running with both waits, the earlier first"""
    later = (STOP + timedelta(hours=4), RESET + timedelta(hours=5))
    begin(repo, handed(), os.getpid())
    wait(repo, 1, STOP, RESET)
    resume(repo, 1)
    wait(repo, 1, *later)
    expected = (Wait(STOP, RESET), Wait(*later))
    assert resume(repo, 1) == Record(handed(), "running", identify(os.getpid()), expected, "")
    assert read(repo)[0].waits == expected


@pytest.mark.supports(
    "test_the_walkthroughs_three_pieces_go_on_through_the_limit_and_show_done_in_a_later_session"
)
def test_end_done_records_the_piece_done_with_its_last_words_and_its_waits(repo: str):
    """Given piece 2 that waited from 01:12 to 04:00 and runs again
    When it's recorded as ended done, with the walkthrough's last words of #15
    Then the record, as given and as read, is done with its wait and those last words"""
    begin(repo, handed(2), os.getpid())
    wait(repo, 2, STOP, RESET)
    resume(repo, 2)
    words = overnight_files.LAST_WORDS[1]
    expected = Record(handed(2), "done", identify(os.getpid()), (Wait(STOP, RESET),), words)
    assert end(repo, 2, "done", words) == expected
    assert read(repo) == [expected]


@pytest.mark.supports("test_a_piece_ended_by_an_error_of_its_own_is_recorded_failed_with_the_error")
def test_end_failed_records_the_piece_failed_with_its_error_as_its_last_words(repo: str):
    """Given piece 1 recorded running, with no wait
    When it's recorded as ended failed, with an error of two lines and words beyond ASCII
    Then the record, as given and as read, is failed with that error whole as its last words"""
    begin(repo, handed(), os.getpid())
    error = 'Reached maximum number of turns (1)\n日付: "2026-02-29"'
    expected = Record(handed(), "failed", identify(os.getpid()), (), error)
    assert end(repo, 1, "failed", error) == expected
    assert read(repo) == [expected]


@pytest.mark.supports("test_a_record_read_while_its_runner_writes_it_is_read_whole_each_time")
@pytest.mark.parametrize(
    "change",
    [
        lambda repo, n: wait(repo, n, STOP, RESET),
        lambda repo, n: resume(repo, n),
        lambda repo, n: end(repo, n, "done", "Done."),
    ],
    ids=["wait", "resume", "end"],
)
def test_a_change_of_a_number_with_no_record_is_refused(repo: str, change):
    """Given a repository with the record of piece 10 alone, whose number starts as 1's does
    When a wait, a run again, or an end of piece 1 is recorded
    Then LookupError is raised, and the record of piece 10 stays as it was"""
    begin(repo, handed(10), os.getpid())
    with pytest.raises(LookupError):
        change(repo, 1)
    assert read(repo) == [running(10)]


# read


@pytest.mark.supports("test_status_with_no_piece_handed_over_shows_no_pieces_yet")
def test_read_of_a_repository_with_no_record_gives_none(repo: str):
    """Given a repository with no `.overnight/`
    When its records are read
    Then none is given"""
    assert read(repo) == []


@pytest.mark.supports(
    "test_the_walkthroughs_three_pieces_go_on_through_the_limit_and_show_done_in_a_later_session"
)
def test_read_gives_several_records_by_their_numbers_whatever_their_days(repo: str):
    """Given the records of pieces 9 and 2 of today, and of piece 10 moved to an earlier day
    When the records are read
    Then they are given as 2, 9, 10"""
    for number in (9, 10, 2):
        begin(repo, handed(number), os.getpid())
    os.rename(folder(repo, 10), folder(repo, 10, "20261120"))
    assert [each.handed.number for each in read(repo)] == [2, 9, 10]


@pytest.mark.supports("test_a_record_left_out_of_its_layout_is_refused_naming_its_file")
@pytest.mark.parametrize(
    "text", ["{not json", "[]", ""], ids=["not JSON", "a list", "empty, as written in part"]
)
def test_read_of_a_record_out_of_its_layout_is_refused_naming_its_file(repo: str, text: str):
    """Given the record of piece 1, which a person then overwrote with text out of its layout
    When the records are read
    Then ValueError is raised, naming the record's file"""
    begin(repo, handed(), os.getpid())
    (name,) = os.listdir(folder(repo, 1))
    with open(os.path.join(folder(repo, 1), name), "w", encoding="utf-8") as f:
        f.write(text)
    with pytest.raises(ValueError, match=name):
        read(repo)
