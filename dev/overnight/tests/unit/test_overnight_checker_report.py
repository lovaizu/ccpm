"""The unit cases of checker/report.py, how overnight tells where a queue's tasks stand: `tell`, of
the walkthrough's morning, its tasks given in the queue's order and told by when each ended, and of
a queue left by a stop, with tasks given up; and `unnamed`, of two versions."""

from __future__ import annotations

import os

import pytest
from checker.report import tell, unnamed
from overnight_bench import (
    FIX_ENDED,
    PAYMENTS_ENDED,
    REFUNDS_ENDED,
    STOPPED,
    WENT_ON,
    Bench,
    checked_text,
    walkthrough_queue,
)
from record.runs import Run, Wait
from record.store import Standing, Stood

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


def stood(b: Bench, runs: list[Run]) -> Standing:
    return Standing(
        False,
        tuple(
            Stood(task, run, os.path.join(b.folder, f"{task.name}.md"))
            for task, run in zip(walkthrough_queue(b).tasks, runs)
        ),
    )


@pytest.mark.supports("test_the_morning_check_shows_each_task_finished_with_its_reply_and_wait")
def test_the_walkthroughs_morning_is_told_as_the_readme_shows_it(b: Bench):
    """Given the walkthrough's tasks in the queue's order, each finished, the review of the payments
    last, after its wait from 00:41 to 01:42, and the fix, which wrote, at 00:28
    When where they stand is told
    Then it is the README's text, each task told by when it ended"""
    standing = stood(
        b,
        [
            Run("finished", "a", 1, (Wait(STOPPED, WENT_ON),), None, PAYMENTS_ENDED, None),
            Run("finished", "b", 0, (), None, REFUNDS_ENDED, None),
            Run("finished", "c", 0, (), None, FIX_ENDED, None),
        ],
    )

    assert tell(b.queue_file, standing) == checked_text(b)


@pytest.mark.supports(
    "test_a_check_after_a_stop_gives_up_the_tasks_left_and_says_how_to_carry_them_on"
)
def test_a_queue_left_by_a_stop_is_told_with_why_each_was_given_up_and_how_to_carry_it_on(b: Bench):
    """Given the walkthrough's tasks, the review of the payments given up by a stop in its session,
    the review of the refunds finished, and the fix given up at its seventh stop at the limit
    When where they stand is told
    Then it counts one finished and two given up, names each why, and how to stack the queue
    again"""
    standing = stood(
        b,
        [
            Run("given up", "a", 0, (), None, STOPPED, "overnight stopped before the task ended"),
            Run("finished", "b", 0, (), None, REFUNDS_ENDED, None),
            Run("given up", "c", 7, (), None, FIX_ENDED, "the usage limit stopped it 7 times"),
        ],
    )

    text = tell(b.queue_file, standing)

    assert text.startswith(f"3 tasks from {b.queue_file}: 1 finished, 2 given up.\n")
    assert "overnight stopped before the task ended" in text
    assert "the usage limit stopped it 7 times" in text
    assert f"/overnight:stack {b.queue_file}" in text


@pytest.mark.supports("test_a_check_naming_no_queue_shows_the_version_and_what_to_name")
@pytest.mark.parametrize("version", ["0.1.0", "1.12.3"])
def test_a_check_naming_no_queue_tells_the_version_and_what_to_name(version: str):
    """Given overnight's version, 0.1.0 or 1.12.3
    When a check that names no stacked queue is told
    Then it says that version and to name the queue file to check"""
    assert unnamed(version).rstrip("\n") == f"overnight {version}: name the queue file to check"


@pytest.mark.supports(
    "test_a_check_while_the_runner_carries_the_queue_tells_the_tasks_not_ended_as_running"
)
def test_a_queue_still_carried_tells_each_task_not_ended_as_running(b: Bench):
    """Given the walkthrough's tasks while their runner carries them: the review of the payments
    waiting for the limit, the review of the refunds finished at 23:52, and the fix waiting for the
    start
    When where they stand is told
    Then each task not yet ended is told as still running, and the review of the refunds by its end
    """
    tasks = stood(
        b,
        [
            Run("waiting for the limit", "a", 1, (Wait(STOPPED, None),), WENT_ON, None, None),
            Run("finished", "b", 0, (), None, REFUNDS_ENDED, None),
            Run("waiting for the start", None, 0, (), None, None, None),
        ],
    )
    standing = Standing(True, tasks.tasks)

    lines = tell(b.queue_file, standing).split("\n")

    for name in ("review-payments", "fix-flaky-checkout"):
        told = [each for each in lines if each.startswith(f"- {name}:")]
        assert len(told) == 1 and "running" in told[0] and "given up" not in told[0]
    assert "- review-refunds: finished at 23:52." in lines
