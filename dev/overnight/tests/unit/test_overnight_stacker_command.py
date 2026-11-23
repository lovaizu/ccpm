"""The unit cases of stacker/command.py, what `queue.py stack` takes and prints: `main`, of one
queue file named whole and from the folder it runs in, of no arguments and of two, and of each
refusal of `stacker.stack.stack`: Refused, ValueError, OSError, and CantStart, each with its exit
code."""

from __future__ import annotations

import os
from typing import Any

import pytest
from overnight_bench import Bench, stacked_text, walkthrough_tasks
from runner.handoff import Carried, Handoff
from stacker import detach, stack
from stacker.command import main
from stacker.queue_file import Fault, Refused, Task

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


def stacked_by(monkeypatch: Any, given: Any) -> list[str]:
    """Puts a stand-in for `stacker.stack.stack` that gives or raises `given`, and gives each path
    it was asked to stack."""
    asked: list[str] = []

    def stand_in(path: str) -> Handoff:
        asked.append(path)
        if isinstance(given, Exception):
            raise given
        return given

    monkeypatch.setattr(stack, "stack", stand_in)
    return asked


def the_handoff(b: Bench) -> Handoff:
    tasks = [Task(t["name"], t["prompt"], t["dir"], t["writes"]) for t in walkthrough_tasks(b)]
    return Handoff(b.queue_file, "23:00", tuple(Carried(task, None) for task in tasks))


@pytest.mark.supports(
    "test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit"
)
def test_a_queue_file_named_whole_prints_the_tasks_stacked_as_the_walkthrough_shows(
    b: Bench, monkeypatch: Any
):
    """Given the walkthrough's queue file, which the stacker takes in
    When `queue.py stack` runs with its whole path
    Then it gives 0 with the README's text, having stacked that path"""
    asked = stacked_by(monkeypatch, the_handoff(b))

    assert main([b.queue_file], b.home) == (0, stacked_text(b.queue_file), "")
    assert asked == [b.queue_file]


@pytest.mark.supports(
    "test_the_walkthroughs_queue_is_stacked_and_each_task_finishes_past_the_limit"
)
def test_a_queue_file_named_from_the_folder_it_runs_in_is_stacked_whole(b: Bench, monkeypatch: Any):
    """Given the walkthrough's queue file, which the stacker takes in
    When `queue.py stack` runs from the user's home with `overnight/tonight.json`
    Then it stacks the whole path, and gives 0 with the README's text naming it whole"""
    asked = stacked_by(monkeypatch, the_handoff(b))

    assert main([os.path.join("overnight", "tonight.json")], b.home) == (
        0,
        stacked_text(b.queue_file),
        "",
    )
    assert asked == [b.queue_file]


@pytest.mark.supports("test_each_skill_runs_its_script_and_shows_what_it_prints")
@pytest.mark.parametrize("argv", [[], ["a.json", "b.json"]], ids=["none", "two"])
def test_arguments_other_than_one_queue_file_give_the_usage(
    b: Bench, monkeypatch: Any, argv: list[str]
):
    """Given no queue file, or two
    When `queue.py stack` runs with them
    Then it gives 2 with the usage, and stacks nothing"""
    asked = stacked_by(monkeypatch, the_handoff(b))

    code, out, err = main(argv, b.home)

    assert (code, "usage" in (out + err).lower()) == (2, True)
    assert asked == []


@pytest.mark.supports("test_a_queue_with_a_prompt_and_a_dir_not_there_is_refused_with_each_fault")
def test_a_queue_refused_gives_1_with_each_fault_and_its_mend(b: Bench, monkeypatch: Any):
    """Given a queue that the stacker refuses for two faults, each with its mend
    When `queue.py stack` runs with it
    Then it gives 1 with each fault and each mend"""
    faults = (
        Fault("the prompt /home/dev/overnight/a.md isn't there", "write it, or name another"),
        Fault("the dir /home/dev/work/b isn't there", "make it, or name another"),
    )
    stacked_by(monkeypatch, Refused(faults))

    code, out, err = main([b.queue_file], b.home)

    assert code == 1
    for each in faults:
        assert each.what in out + err and each.mend in out + err


@pytest.mark.supports("test_a_runs_file_out_of_form_refuses_the_stacking")
def test_a_runs_file_out_of_form_gives_1_with_whats_wrong(b: Bench, monkeypatch: Any):
    """Given a queue whose runs' file the stacker finds out of form
    When `queue.py stack` runs with it
    Then it gives 1 with what's wrong"""
    stacked_by(monkeypatch, ValueError("/home/dev/overnight/tonight/runs.json: isn't JSON"))

    code, out, err = main([b.queue_file], b.home)

    assert code == 1 and "/home/dev/overnight/tonight/runs.json: isn't JSON" in out + err


@pytest.mark.supports("test_a_runner_that_the_os_doesnt_start_leaves_the_record_to_carry_on")
@pytest.mark.parametrize(
    "error",
    [
        OSError(28, "No space left on device"),
        detach.CantStart("fork: Resource temporarily unavailable"),
    ],
    ids=["OSError", "CantStart"],
)
def test_what_the_os_refused_gives_2_with_what_it_said(
    b: Bench, monkeypatch: Any, error: Exception
):
    """Given a queue whose record the OS doesn't let be written, or whose runner it doesn't start
    When `queue.py stack` runs with it
    Then it gives 2 with what the OS said"""
    stacked_by(monkeypatch, error)

    code, out, err = main([b.queue_file], b.home)

    said = "No space left on device" if isinstance(error, OSError) else "Resource temporarily"
    assert code == 2 and said in out + err


@pytest.mark.supports("test_a_queue_whose_every_task_finished_stacked_again_starts_no_runner")
def test_a_queue_whose_every_task_finished_gives_0_saying_so(b: Bench, monkeypatch: Any):
    """Given the walkthrough's queue file, whose every task finished, so the stacker hands no task
    When `queue.py stack` runs with it
    Then it gives 0 saying that every task finished, and not that any task was stacked"""
    stacked_by(monkeypatch, Handoff(b.queue_file, None, ()))

    code, out, _ = main([b.queue_file], b.home)

    assert code == 0 and "finished" in out
    assert out != stacked_text(b.queue_file) and not out.startswith("Stacked 3")
