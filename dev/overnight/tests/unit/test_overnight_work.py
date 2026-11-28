"""The cases of one work's runs: done, retried in the same conversation after growing waits, or
failed once its retries run out, which support the cases of the `overnight` command in
test_overnight_command.py."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

from claude import claude_double
from overnight import record, work

PROMPT = "Move the tests in tests/unittest_old/ to pytest"
TOOLS = "Read,Edit,Bash(pytest:*)"
SESSION_ID = claude_double.SESSION_ID


class Clock:
    """A clock that stands at 23:00:12 on 28 November 2026 and moves only by what overnight
    sleeps."""

    def __init__(self) -> None:
        self.time = datetime(2026, 11, 28, 23, 0, 12)

    def now(self) -> datetime:
        return self.time

    def sleep(self, seconds: float) -> None:
        self.time += timedelta(seconds=seconds)


def test_a_work_whose_first_run_ends_with_no_error_is_done_after_one_run(
    double: claude_double.Double, work_dir: str
) -> None:
    """Given a work whose first run ends with no error
    When overnight carries it
    Then the work is done after 1 run, in the run's conversation, and its log says so."""
    double.answer(claude_double.DONE)

    folder = carry(work_dir, 7)

    assert (state_of(folder), log_of(folder)) == (
        {"status": "done", "dir": work_dir, "session_id": SESSION_ID, "runs": 1},
        "23:00 run 1 started\n23:00 run 1 done\nwork 20261128-230012 done after 1 run\n",
    )


def test_a_stopped_run_is_retried_after_5_minutes_until_done(
    double: claude_double.Double, work_dir: str
) -> None:
    """Given a work whose first run the usage limit stops, and whose second ends with no error
    When overnight carries it
    Then the work is done after 2 runs, the second 5 minutes after the stop, and its log says why
    the first stopped and when the retry is."""
    double.answer(claude_double.LIMIT, claude_double.RESUMED)

    folder = carry(work_dir, 7)

    assert (state_of(folder), log_of(folder)) == (
        {"status": "done", "dir": work_dir, "session_id": SESSION_ID, "runs": 2},
        (
            "23:00 run 1 started\n"
            f"23:00 run 1 stopped: {claude_double.LIMIT_TEXT}. Retry 1 of 7 at 23:05.\n"
            "23:05 run 2 started\n"
            "23:05 run 2 done\n"
            "work 20261128-230012 done after 2 runs\n"
        ),
    )


def test_a_retry_asks_claude_to_go_on_in_the_conversation_of_the_stop(
    double: claude_double.Double, work_dir: str
) -> None:
    """Given a work whose first run the usage limit stops in a conversation
    When overnight retries it
    Then it asks Claude Code to go on, by --resume in that conversation, in the work's folder."""
    double.answer(claude_double.LIMIT, claude_double.RESUMED)

    carry(work_dir, 7)

    retry = double.calls()[1]
    assert (retry["args"][-2:], retry["stdin"], retry["cwd"]) == (
        ["--resume", SESSION_ID],
        work.GO_ON,
        work_dir,
    )


def test_a_work_waiting_for_its_retry_is_recorded_as_running_after_its_runs(
    double: claude_double.Double, work_dir: str
) -> None:
    """Given a work whose first run the usage limit stops in a conversation
    When overnight waits for its retry
    Then the work's state.json says it's running, in that conversation, after 1 run."""
    double.answer(claude_double.LIMIT, claude_double.RESUMED)
    clock = Clock()
    folder = record.start(clock.now(), work_dir)
    seen: list[dict[str, object]] = []

    work.carry(
        folder,
        work.Work(work_dir, TOOLS, PROMPT, 7),
        work.Clock(clock.now, lambda seconds: seen.append(state_of(folder))),
    )

    assert seen == [{"status": "running", "dir": work_dir, "session_id": SESSION_ID, "runs": 1}]


def test_a_work_whose_folder_is_gone_is_retried_then_failed(
    double: claude_double.Double, work_dir: str
) -> None:
    """Given a work with 1 retry, whose folder is gone before its first run
    When overnight carries it
    Then each run stops because claude couldn't start, and the work is failed after 2 runs."""
    double.answer(claude_double.DONE, claude_double.DONE)
    os.rmdir(work_dir)

    folder = carry(work_dir, 1)

    stop = f"claude couldn't start: No such file or directory: {work_dir}"
    assert (state_of(folder), log_of(folder)) == (
        {"status": "failed", "dir": work_dir, "session_id": None, "runs": 2},
        (
            "23:00 run 1 started\n"
            f"23:00 run 1 stopped: {stop}. Retry 1 of 1 at 23:05.\n"
            "23:05 run 2 started\n"
            f"23:05 run 2 stopped: {stop}. No retries left.\n"
            "work 20261128-230012 failed after 2 runs\n"
        ),
    )


def test_the_waits_are_5_then_10_then_60_minutes_each(
    double: claude_double.Double, work_dir: str
) -> None:
    """Given a work whose first 4 runs the usage limit stops
    When overnight retries it
    Then it waits 5 minutes before the first retry, 10 before the second, and 60 before each
    after that."""
    double.answer(
        claude_double.LIMIT,
        claude_double.LIMIT,
        claude_double.LIMIT,
        claude_double.LIMIT,
        claude_double.RESUMED,
    )

    folder = carry(work_dir, 7)

    assert log_of(folder) == (
        "23:00 run 1 started\n"
        f"23:00 run 1 stopped: {claude_double.LIMIT_TEXT}. Retry 1 of 7 at 23:05.\n"
        "23:05 run 2 started\n"
        f"23:05 run 2 stopped: {claude_double.LIMIT_TEXT}. Retry 2 of 7 at 23:15.\n"
        "23:15 run 3 started\n"
        f"23:15 run 3 stopped: {claude_double.LIMIT_TEXT}. Retry 3 of 7 at 00:15.\n"
        "00:15 run 4 started\n"
        f"00:15 run 4 stopped: {claude_double.LIMIT_TEXT}. Retry 4 of 7 at 01:15.\n"
        "01:15 run 5 started\n"
        "01:15 run 5 done\n"
        "work 20261128-230012 done after 5 runs\n"
    )


def test_a_work_done_on_its_last_retry_is_done(double: claude_double.Double, work_dir: str) -> None:
    """Given a work with 1 retry, whose first run the usage limit stops
    When its one retry ends with no error
    Then the work is done after 2 runs."""
    double.answer(claude_double.LIMIT, claude_double.RESUMED)

    folder = carry(work_dir, 1)

    assert state_of(folder) == {
        "status": "done",
        "dir": work_dir,
        "session_id": SESSION_ID,
        "runs": 2,
    }


def test_a_work_stopped_once_more_than_its_retries_is_failed(
    double: claude_double.Double, work_dir: str
) -> None:
    """Given a work with 1 retry, whose runs the usage limit stops each time
    When its one retry stops too
    Then the work is failed after 2 runs, and its log says no retries are left."""
    double.answer(claude_double.LIMIT, claude_double.LIMIT)

    folder = carry(work_dir, 1)

    assert (state_of(folder), log_of(folder)) == (
        {"status": "failed", "dir": work_dir, "session_id": SESSION_ID, "runs": 2},
        (
            "23:00 run 1 started\n"
            f"23:00 run 1 stopped: {claude_double.LIMIT_TEXT}. Retry 1 of 1 at 23:05.\n"
            "23:05 run 2 started\n"
            f"23:05 run 2 stopped: {claude_double.LIMIT_TEXT}. No retries left.\n"
            "work 20261128-230012 failed after 2 runs\n"
        ),
    )


def test_a_work_with_no_retries_is_failed_at_its_first_stop(
    double: claude_double.Double, work_dir: str
) -> None:
    """Given a work with 0 retries
    When the usage limit stops its first run
    Then the work is failed after 1 run, with no retry."""
    double.answer(claude_double.LIMIT)

    folder = carry(work_dir, 0)

    assert (state_of(folder), log_of(folder)) == (
        {"status": "failed", "dir": work_dir, "session_id": SESSION_ID, "runs": 1},
        (
            "23:00 run 1 started\n"
            f"23:00 run 1 stopped: {claude_double.LIMIT_TEXT}. No retries left.\n"
            "work 20261128-230012 failed after 1 run\n"
        ),
    )


def test_a_run_stopped_before_its_conversation_is_known_is_asked_anew(
    double: claude_double.Double, work_dir: str
) -> None:
    """Given a work whose first run a signal kills before Claude Code names its conversation
    When overnight retries it
    Then it asks Claude Code for the work's prompt in a new conversation."""
    double.answer(claude_double.KILLED, claude_double.DONE)

    carry(work_dir, 7)

    retry = double.calls()[1]
    assert (retry["args"], retry["stdin"]) == (
        ["-p", "--output-format", "json", "--allowed-tools", TOOLS],
        PROMPT,
    )


def test_a_retry_that_names_no_conversation_keeps_the_one_known(
    double: claude_double.Double, work_dir: str
) -> None:
    """Given a work whose first run stopped in a conversation, and whose retry stopped naming none
    When overnight retries it again
    Then it asks Claude Code to go on in the conversation of the first run."""
    double.answer(claude_double.LIMIT, claude_double.NO_CONVERSATION, claude_double.RESUMED)

    carry(work_dir, 7)

    assert double.calls()[2]["args"][-2:] == ["--resume", SESSION_ID]


def test_main_carries_the_work_that_its_arguments_name(
    double: claude_double.Double, work_dir: str
) -> None:
    """Given a work's folder, the folder it runs in, its tools, its retries, and its prompt, as the
    command passes them
    When the work's main runs
    Then it carries that work to its end."""
    double.answer(claude_double.DONE)
    folder = record.start(Clock().now(), work_dir)

    work.main([folder, work_dir, TOOLS, "7", PROMPT])

    call = double.calls()[0]
    assert (state_of(folder)["status"], call["args"][-1], call["stdin"], call["cwd"]) == (
        "done",
        TOOLS,
        PROMPT,
        work_dir,
    )


def carry(work_dir: str, retries: int) -> str:
    clock = Clock()
    folder = record.start(clock.now(), work_dir)
    work.carry(
        folder,
        work.Work(work_dir, TOOLS, PROMPT, retries),
        work.Clock(clock.now, clock.sleep),
    )
    return folder


def state_of(folder: str) -> dict[str, object]:
    with open(os.path.join(folder, record.STATE), encoding="utf-8") as f:
        return json.load(f)


def log_of(folder: str) -> str:
    with open(os.path.join(folder, record.LOG), encoding="utf-8") as f:
        return f.read()
