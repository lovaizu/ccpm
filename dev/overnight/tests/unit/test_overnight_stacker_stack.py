"""The unit cases of stacker/stack.py, the steps of stacking a queue: `stack`, of the walkthrough's
queue never stacked, of one left by a stop, of one whose every task finished, and each refusal: a
task that can't start, a runner still carrying the queue, a runs' file out of form, a folder that
can't be written, and a runner that the OS doesn't start, with the record it leaves."""

from __future__ import annotations

import os
from typing import Any

import pytest
from overnight_bench import (
    REFUNDS_ENDED,
    STOPPED,
    Bench,
    held_elsewhere,
    keep,
    no_sandbox,
    run_json,
    walkthrough_queue,
    walkthrough_tasks,
)
from runner import handoff
from runner.handoff import Carried, Handoff
from stacker import detach
from stacker.queue_file import Refused
from stacker.stack import stack

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


def started(b: Bench) -> list[Handoff]:
    """Each handoff that the runner was started with."""
    return [handoff.decode(each) for each in b.handed]


@pytest.mark.supports(
    "test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit"
)
def test_a_queue_never_stacked_is_written_and_handed_to_its_runner_whole(b: Bench):
    """Given the walkthrough's queue, never stacked
    When it is stacked
    Then it gives what the runner was handed: the queue file, 23:00, and each task to start anew;
    the runner is started once with that; and each task waits for the start in the record"""
    given = stack(b.queue_file)

    expected = Handoff(
        b.queue_file, "23:00", tuple(Carried(task, None) for task in walkthrough_queue(b).tasks)
    )
    assert given == expected
    assert started(b) == [expected]
    assert [each["run"] for each in b.runs()] == [
        {"state": "waiting for the start", "stops": 0, "waits": []}
    ] * 3


@pytest.mark.supports("test_stacking_again_carries_on_each_unfinished_task_in_its_session")
def test_a_queue_left_by_a_stop_hands_its_runner_each_unfinished_task_with_its_session(b: Bench):
    """Given the walkthrough's queue left by a stop, with no lock held: the review of the payments
    running in its session, the review of the refunds finished, and the fix given up before it
    started
    When it is stacked again
    Then the runner is handed no start, so that it starts at once, the review of the payments in
    its session, and the fix anew, and the review of the refunds is left finished as it ended"""
    payments, refunds, fix = walkthrough_tasks(b)
    refunded = run_json("finished", session="r", ended=REFUNDS_ENDED)
    keep(
        b,
        [
            (payments, run_json("running", session="s")),
            (refunds, refunded),
            (fix, run_json("given up", ended=STOPPED, why="overnight stopped")),
        ],
    )

    given = stack(b.queue_file)

    first, _, third = walkthrough_queue(b).tasks
    assert given == Handoff(b.queue_file, None, (Carried(first, "s"), Carried(third, None)))
    assert started(b) == [given]
    assert b.run_of("review-refunds") == refunded


@pytest.mark.supports("test_stacking_again_carries_on_each_unfinished_task_in_its_session")
def test_a_queue_whose_every_task_finished_starts_no_runner(b: Bench):
    """Given the walkthrough's queue whose every task finished
    When it is stacked again
    Then it gives no task to carry, starts no runner, and leaves each run as it ended"""
    keep(
        b,
        [
            (task, run_json("finished", session="s", ended=REFUNDS_ENDED))
            for task in walkthrough_tasks(b)
        ],
    )
    before = b.runs()

    assert stack(b.queue_file).tasks == ()
    assert b.handed == []
    assert b.runs() == before


@pytest.mark.supports(
    "test_a_queue_with_a_prompt_and_a_dir_not_there_is_refused_with_each_fault",
    "test_a_queue_with_one_task_that_cant_start_runs_no_task",
)
def test_a_task_that_cant_start_refuses_the_queue_writing_and_starting_nothing(b: Bench):
    """Given the walkthrough's queue whose fix's prompt isn't there
    When it is stacked
    Then it refuses with Refused naming the prompt, writes no record, and starts no runner"""
    os.remove(b.path("overnight", "fix-flaky-checkout.md"))

    with pytest.raises(Refused) as refused:
        stack(b.queue_file)

    assert any(
        b.path("overnight", "fix-flaky-checkout.md") in each.what for each in refused.value.faults
    )
    assert not os.path.exists(b.folder)
    assert b.handed == []


@pytest.mark.supports("test_a_writing_task_where_the_sandbox_cant_run_is_refused_at_stacking")
def test_a_writing_task_where_the_sandbox_cant_hold_refuses_the_queue(b: Bench):
    """Given the walkthrough's queue, whose fix writes, on a computer where the sandbox can't run
    When it is stacked
    Then it refuses with Refused naming the fix, writes no record, and starts no runner"""
    no_sandbox(b)

    with pytest.raises(Refused) as refused:
        stack(b.queue_file)

    assert any("fix-flaky-checkout" in each.what for each in refused.value.faults)
    assert not os.path.exists(b.folder)
    assert b.handed == []


@pytest.mark.supports(
    "test_a_queue_whose_runner_still_carries_it_is_refused_with_where_its_tasks_stand"
)
def test_a_queue_whose_runner_still_carries_it_is_refused_leaving_its_record(b: Bench):
    """Given the walkthrough's queue, stacked, whose runner still holds its lock
    When it is stacked again
    Then it refuses with Refused, leaves the record as it was, and starts no other runner"""
    stack(b.queue_file)
    before = b.runs()

    with held_elsewhere(b.queue_file), pytest.raises(Refused):
        stack(b.queue_file)

    assert b.runs() == before
    assert len(b.handed) == 1


@pytest.mark.supports("test_a_runs_file_out_of_form_refuses_the_stacking")
def test_a_runs_file_out_of_form_refuses_the_queue_naming_it(b: Bench):
    """Given the walkthrough's queue whose `runs.json` isn't JSON
    When it is stacked
    Then it refuses with ValueError naming the file, leaves it as it was, and starts no runner"""
    path = b.write(os.path.join(b.folder, "runs.json"), "{")

    with pytest.raises(ValueError, match="runs.json"):
        stack(b.queue_file)

    with open(path, encoding="utf-8") as f:
        assert f.read() == "{"
    assert b.handed == []


@pytest.mark.supports("test_a_runner_that_the_os_doesnt_start_leaves_the_record_to_carry_on")
def test_a_folder_that_cant_be_written_refuses_the_queue_starting_nothing(b: Bench):
    """Given the walkthrough's queue, where a file lies in place of its folder
    When it is stacked
    Then it refuses with OSError, and starts no runner"""
    b.write(b.folder, "in the way")

    with pytest.raises(OSError):
        stack(b.queue_file)

    assert b.handed == []


@pytest.mark.supports("test_a_runner_that_the_os_doesnt_start_leaves_the_record_to_carry_on")
def test_a_runner_the_os_doesnt_start_is_refused_leaving_the_record_written(
    b: Bench, monkeypatch: Any
):
    """Given the walkthrough's queue, on a computer that doesn't start the runner
    When it is stacked
    Then it refuses with CantStart, and the record holds each task waiting for the start"""

    def refused(given: Handoff) -> None:
        raise detach.CantStart("fork: Resource temporarily unavailable")

    monkeypatch.setattr(detach, "start_runner", refused)

    with pytest.raises(detach.CantStart):
        stack(b.queue_file)

    assert [each["run"]["state"] for each in b.runs()] == ["waiting for the start"] * 3
