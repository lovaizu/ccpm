"""The unit cases of record/runs.py, how a queue's runs lie on disk: `load`, of no file, of the
walkthrough's morning, of none, one, and several tasks, of a run of each state with and without
each field it may lack, and each refusal: a file that isn't JSON, that lacks `tasks`, whose run has
a state of no name, a negative count of stops, a field of no name, or a moment that isn't one; and
`dump`, of none and of the walkthrough's runs, read back by `load`, with no field of a value it
lacks."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
from overnight_bench import (
    PAYMENTS_ENDED,
    STOPPED,
    WENT_ON,
    run_json,
    task_json,
    wait_json,
)
from record.runs import Kept, Run, Wait, dump, load
from stacker.queue_file import Task

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")

PAYMENTS = task_json(
    "review-payments", "/home/dev/overnight/review-payments.md", "/home/dev/work/shop"
)
FIX = task_json(
    "fix-flaky-checkout",
    "/home/dev/overnight/fix-flaky-checkout.md",
    "/home/dev/work/shop-fix-flaky-checkout",
    True,
)


def written(tmp_path: Any, tasks: list[dict[str, Any]]) -> str:
    """Writes `runs.json` of the tasks, as overnight leaves it, and gives its path."""
    path = os.path.join(str(tmp_path), "runs.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"tasks": tasks}, f)
    return path


def task_of(given: dict[str, Any]) -> Task:
    return Task(given["name"], given["prompt"], given["dir"], given["writes"])


@pytest.mark.supports("test_each_task_and_reply_lies_beside_the_queue_file_for_a_later_session")
def test_no_runs_file_loads_as_none(tmp_path: Any):
    """Given a queue's folder with no `runs.json`
    When its runs are loaded
    Then it gives None"""
    assert load(os.path.join(str(tmp_path), "runs.json")) is None


@pytest.mark.supports("test_each_task_and_reply_lies_beside_the_queue_file_for_a_later_session")
def test_no_tasks_load_as_none_kept(tmp_path: Any):
    """Given a `runs.json` of no task
    When its runs are loaded
    Then it gives no task"""
    assert load(written(tmp_path, [])) == ()


@pytest.mark.supports("test_each_task_and_reply_lies_beside_the_queue_file_for_a_later_session")
def test_a_finished_run_after_a_wait_loads_with_each_field(tmp_path: Any):
    """Given a `runs.json` of the review of the payments, finished at 02:16 after one wait from
    00:41 to 01:42, in its session
    When its runs are loaded
    Then it gives the task with its run whole, each moment with its offset"""
    run = run_json(
        "finished",
        session="1b4e28ba",
        stops=1,
        waits=[wait_json(STOPPED, WENT_ON)],
        ended=PAYMENTS_ENDED,
    )

    kept = load(written(tmp_path, [{"task": PAYMENTS, "run": run}]))

    assert kept == (
        Kept(
            task_of(PAYMENTS),
            Run("finished", "1b4e28ba", 1, (Wait(STOPPED, WENT_ON),), None, PAYMENTS_ENDED, None),
        ),
    )


@pytest.mark.supports("test_each_task_and_reply_lies_beside_the_queue_file_for_a_later_session")
def test_several_tasks_load_in_the_queues_order(tmp_path: Any):
    """Given a `runs.json` of the fix waiting for the start, then the review given up with why
    When its runs are loaded
    Then it gives the fix first and the review second, each field each lacks None"""
    tasks = [
        {"task": FIX, "run": run_json("waiting for the start")},
        {"task": PAYMENTS, "run": run_json("given up", session="s", ended=STOPPED, why="w")},
    ]

    kept = load(written(tmp_path, tasks))

    assert kept == (
        Kept(task_of(FIX), Run("waiting for the start", None, 0, (), None, None, None)),
        Kept(task_of(PAYMENTS), Run("given up", "s", 0, (), None, STOPPED, "w")),
    )


@pytest.mark.supports("test_a_task_waiting_for_the_limit_stands_waiting_until_it_goes_on")
def test_a_run_waiting_for_the_limit_loads_its_open_wait_and_when_it_goes_on(tmp_path: Any):
    """Given a `runs.json` of the review waiting for the limit until 01:42, after two waits, the
    second still open
    When its runs are loaded
    Then it gives both waits, the second with no moment it went on, and the moment it goes on"""
    run = run_json(
        "waiting for the limit",
        session="s",
        stops=2,
        waits=[wait_json(STOPPED, WENT_ON), wait_json(PAYMENTS_ENDED)],
        until=WENT_ON,
    )

    kept = load(written(tmp_path, [{"task": PAYMENTS, "run": run}]))

    assert kept is not None
    assert kept[0].run == Run(
        "waiting for the limit",
        "s",
        2,
        (Wait(STOPPED, WENT_ON), Wait(PAYMENTS_ENDED, None)),
        WENT_ON,
        None,
        None,
    )


@pytest.mark.supports(
    "test_a_runs_file_out_of_form_refuses_the_stacking",
    "test_a_check_of_a_runs_file_out_of_form_says_whats_wrong",
)
@pytest.mark.parametrize(
    "text",
    [
        "{not json",
        json.dumps({"runs": []}),
        json.dumps({"tasks": [{"task": PAYMENTS, "run": run_json("paused")}]}),
        json.dumps({"tasks": [{"task": PAYMENTS, "run": run_json("running", stops=-1)}]}),
        json.dumps({"tasks": [{"task": PAYMENTS, "run": run_json("running", pid=12)}]}),
        json.dumps({"tasks": [{"task": PAYMENTS, "run": run_json("finished", ended="at night")}]}),
        json.dumps({"tasks": [{"task": {**PAYMENTS, "writes": "no"}, "run": run_json("running")}]}),
    ],
    ids=["not JSON", "no tasks", "no state", "stops", "field", "moment", "writes"],
)
def test_a_runs_file_out_of_form_is_refused_naming_it(tmp_path: Any, text: str):
    """Given a `runs.json` that isn't JSON, lacks `tasks`, or holds a run of a state of no name, a
    negative count of stops, a field of no name, or a moment that isn't one, or a task whose
    `writes` isn't true or false
    When its runs are loaded
    Then it refuses with ValueError naming the file"""
    path = os.path.join(str(tmp_path), "runs.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    with pytest.raises(ValueError, match=path.replace("\\", "\\\\")):
        load(path)


@pytest.mark.supports("test_each_task_and_reply_lies_beside_the_queue_file_for_a_later_session")
def test_no_tasks_dump_as_a_runs_file_of_none():
    """Given no task
    When its runs' file is dumped
    Then its text is JSON of an empty `tasks`"""
    assert json.loads(dump(())) == {"tasks": []}


@pytest.mark.supports("test_each_task_and_reply_lies_beside_the_queue_file_for_a_later_session")
def test_runs_dump_as_their_file_with_no_field_they_lack(tmp_path: Any):
    """Given the review finished after a wait, and the fix waiting for the start
    When their runs' file is dumped, and loaded back
    Then its text holds each task and run as `runs.json` holds them, no field of a value they
    lack, and loads back to the same runs"""
    kept = (
        Kept(
            task_of(PAYMENTS),
            Run("finished", "s", 1, (Wait(STOPPED, WENT_ON),), None, PAYMENTS_ENDED, None),
        ),
        Kept(task_of(FIX), Run("waiting for the start", None, 0, (), None, None, None)),
    )

    text = dump(kept)

    tasks = json.loads(text)["tasks"]
    assert [each["task"] for each in tasks] == [PAYMENTS, FIX]
    assert tasks[1]["run"] == {"state": "waiting for the start", "stops": 0, "waits": []}
    assert sorted(tasks[0]["run"]) == ["ended", "session", "state", "stops", "waits"]
    path = written(tmp_path, tasks)
    assert load(path) == kept
