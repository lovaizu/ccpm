"""The unit cases of stacker/admission.py, which queue can be taken in: `faults`, of a queue whose
tasks can each start, never stacked and stacked with no runner, and of each fault alone and
together: a prompt's file not there, or a folder in its place, a dir not there, or a file in its
place, a writing task and a reading one where the sandbox can't hold, and a queue whose runner
still carries it, among none, one, and several tasks at fault."""

from __future__ import annotations

import os
from typing import Any

import pytest
from overnight_bench import Bench, walkthrough_queue
from record.runs import Run, State
from record.store import Standing, Stood
from stacker.admission import faults
from stacker.queue_file import Fault, Queue

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


def standing(queue: Queue, carried: bool, state: State = "waiting for the start") -> Standing:
    run = Run(state, None, 0, (), None, None, None)
    return Standing(carried, tuple(Stood(task, run, task.name + ".md") for task in queue.tasks))


def naming(found: tuple[Fault, ...], word: str) -> list[Fault]:
    return [each for each in found if word in each.what + each.mend]


@pytest.mark.supports("test_a_queue_with_a_prompt_and_a_dir_not_there_is_refused_with_each_fault")
@pytest.mark.parametrize("carried", [None, False], ids=["never stacked", "stacked, no runner"])
def test_a_queue_whose_tasks_can_each_start_has_no_fault(b: Bench, carried: Any):
    """Given the walkthrough's queue whose prompts and dirs are there, where the sandbox holds,
    never stacked or stacked with no runner carrying it
    When its faults are found
    Then it has none"""
    queue = walkthrough_queue(b)
    given = None if carried is None else standing(queue, carried)

    assert faults(queue, given, True) == ()


@pytest.mark.supports(
    "test_a_queue_with_a_prompt_and_a_dir_not_there_is_refused_with_each_fault",
    "test_a_queue_with_one_task_that_cant_start_runs_no_task",
)
def test_a_prompt_not_there_is_a_fault_naming_it_with_its_mend(b: Bench):
    """Given the walkthrough's queue whose review of the refunds names a prompt's file not there
    When its faults are found
    Then there is one, naming that file, with its mend"""
    os.remove(b.path("overnight", "review-refunds.md"))

    found = faults(walkthrough_queue(b), None, True)

    assert len(found) == 1
    assert naming(found, b.path("overnight", "review-refunds.md")) and found[0].mend


@pytest.mark.supports("test_a_queue_with_a_prompt_and_a_dir_not_there_is_refused_with_each_fault")
def test_a_folder_in_place_of_a_prompt_is_a_fault(b: Bench):
    """Given the walkthrough's queue whose review of the refunds names a folder as its prompt
    When its faults are found
    Then there is one, naming that path"""
    os.remove(b.path("overnight", "review-refunds.md"))
    os.makedirs(b.path("overnight", "review-refunds.md"))

    found = faults(walkthrough_queue(b), None, True)

    assert len(found) == 1 and naming(found, b.path("overnight", "review-refunds.md"))


@pytest.mark.supports("test_a_queue_with_a_prompt_and_a_dir_not_there_is_refused_with_each_fault")
def test_a_dir_not_there_or_a_file_in_its_place_is_a_fault(b: Bench):
    """Given the walkthrough's queue whose reviews' dir isn't there, and a queue whose dir is a file
    When the faults of each are found
    Then each has a fault for each of the two tasks of that dir, naming it"""
    os.rename(b.path("work", "shop"), b.path("work", "moved"))
    gone = faults(walkthrough_queue(b), None, True)
    b.write(b.path("work", "shop"), "a file")
    a_file = faults(walkthrough_queue(b), None, True)

    for found in (gone, a_file):
        assert len(found) == 2
        assert len(naming(found, b.path("work", "shop"))) == 2


@pytest.mark.supports("test_a_writing_task_where_the_sandbox_cant_run_is_refused_at_stacking")
def test_a_writing_task_where_the_sandbox_cant_hold_is_a_fault_and_a_reading_one_isnt(b: Bench):
    """Given the walkthrough's queue, whose fix alone writes, where the sandbox can't hold
    When its faults are found
    Then there is one, naming the fix"""
    found = faults(walkthrough_queue(b), None, False)

    assert len(found) == 1 and naming(found, "fix-flaky-checkout")


@pytest.mark.supports("test_a_writing_task_where_the_sandbox_cant_run_is_refused_at_stacking")
def test_a_queue_of_reading_tasks_where_the_sandbox_cant_hold_has_no_fault(b: Bench):
    """Given a queue of the two reviews alone, where the sandbox can't hold
    When its faults are found
    Then it has none"""
    queue = walkthrough_queue(b)
    reading = Queue(queue.path, queue.start, queue.tasks[:2])

    assert faults(reading, None, False) == ()


@pytest.mark.supports(
    "test_a_queue_whose_runner_still_carries_it_is_refused_with_where_its_tasks_stand"
)
def test_a_queue_whose_runner_still_carries_it_is_a_fault_with_where_its_tasks_stand(b: Bench):
    """Given the walkthrough's queue whose runner still carries it, each task running
    When its faults are found
    Then there is one, naming each task and where it stands"""
    queue = walkthrough_queue(b)

    found = faults(queue, standing(queue, True, "running"), True)

    assert len(found) == 1
    for task in queue.tasks:
        assert naming(found, task.name)
    assert naming(found, "running")


@pytest.mark.supports("test_a_queue_with_a_prompt_and_a_dir_not_there_is_refused_with_each_fault")
def test_each_fault_of_several_tasks_is_found_together(b: Bench):
    """Given the walkthrough's queue whose review of the payments names a prompt not there, whose
    fix's dir isn't there, where the sandbox can't hold, and whose runner still carries it
    When its faults are found
    Then a fault names each: the prompt, the dir, the fix that writes, and where the tasks stand"""
    os.remove(b.path("overnight", "review-payments.md"))
    os.rename(b.path("work", "shop-fix-flaky-checkout"), b.path("work", "moved"))
    queue = walkthrough_queue(b)

    found = faults(queue, standing(queue, True, "running"), False)

    assert naming(found, b.path("overnight", "review-payments.md"))
    assert naming(found, b.path("work", "shop-fix-flaky-checkout"))
    assert naming(found, "running")
    assert len(found) >= 4
