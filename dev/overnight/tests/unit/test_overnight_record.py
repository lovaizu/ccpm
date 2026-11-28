"""The cases of where a work's state and log lie and the form of each, which support the cases of
the `overnight` command in test_overnight_command.py."""

from __future__ import annotations

import json
import os
from datetime import datetime

from overnight import record

START = datetime(2026, 11, 28, 23, 0, 12)


def test_a_new_work_gets_a_folder_named_by_its_start_under_the_users_state(home: str) -> None:
    """Given no work started yet
    When overnight starts a work at 23:00:12 on 28 November 2026
    Then the work's folder is ~/.local/state/overnight/20261128-230012."""
    folder = record.start(START, "/home/you/work/shop")

    assert folder == os.path.join(home, ".local", "state", "overnight", "20261128-230012")


def test_a_work_started_in_the_same_second_as_another_gets_a_folder_of_its_own(home: str) -> None:
    """Given a work started at 23:00:12 on 28 November 2026
    When overnight starts a second work in the same second
    Then the second work's folder is ~/.local/state/overnight/20261128-230012-2."""
    record.start(START, "/home/you/work/shop")

    folder = record.start(START, "/home/you/work/shop")

    assert folder == os.path.join(home, ".local", "state", "overnight", "20261128-230012-2")


def test_a_third_work_started_in_the_same_second_gets_the_next_number(home: str) -> None:
    """Given two works started at 23:00:12 on 28 November 2026
    When overnight starts a third work in the same second
    Then the third work's folder is ~/.local/state/overnight/20261128-230012-3."""
    record.start(START, "/home/you/work/shop")
    record.start(START, "/home/you/work/shop")

    folder = record.start(START, "/home/you/work/shop")

    assert folder == os.path.join(home, ".local", "state", "overnight", "20261128-230012-3")


def test_a_new_work_is_recorded_as_running_with_no_runs_yet(work_dir: str) -> None:
    """Given no work started yet
    When overnight starts a work in a folder
    Then the work's state.json says it's running in that folder, with no conversation and no
    runs yet."""
    folder = record.start(START, work_dir)

    assert state_of(folder) == {
        "status": "running",
        "dir": work_dir,
        "session_id": None,
        "runs": 0,
    }


def test_a_work_written_again_holds_only_its_new_state(work_dir: str) -> None:
    """Given a work recorded as running
    When overnight records it as done after 6 runs
    Then the work's state.json holds the new state alone."""
    folder = record.start(START, work_dir)

    record.write(folder, record.State("done", work_dir, "8d1e5b7a", 6))

    assert state_of(folder) == {
        "status": "done",
        "dir": work_dir,
        "session_id": "8d1e5b7a",
        "runs": 6,
    }


def test_a_line_logged_goes_after_the_lines_before_it(work_dir: str) -> None:
    """Given a work whose log holds a line
    When overnight logs another line
    Then the log holds both lines, in the order logged, each ending with a newline."""
    folder = record.start(START, work_dir)
    record.log(folder, "23:00 run 1 started")

    record.log(folder, "23:00 run 1 done")

    assert log_of(folder) == "23:00 run 1 started\n23:00 run 1 done\n"


def state_of(folder: str) -> object:
    with open(os.path.join(folder, "state.json"), encoding="utf-8") as f:
        return json.load(f)


def log_of(folder: str) -> str:
    with open(os.path.join(folder, "log"), encoding="utf-8") as f:
        return f.read()
