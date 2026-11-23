"""What overnight's integration cases share: a bench for each case, and the fixture `broken`, which
takes the part that holds a case's principle item out of overnight where TRACE_BROKEN is 1, as the
plugin guide's A principle's test seen to fail says. A part taken out is an interface given again in
its module for the case alone, wrapping or replacing the one there, so that the parts run without
what holds the item."""

from __future__ import annotations

import dataclasses
import os
import shutil
from collections.abc import Callable
from datetime import timedelta
from typing import Any

import overnight_bench
import pytest
from overnight_bench import ATTACHED, Bench, Detached


@pytest.fixture
def b(tmp_path: Any, monkeypatch: Any) -> Bench:
    """The bench: the user's folders, with the doubles of Claude Code and the clock in their
    places."""
    return overnight_bench.bench(str(tmp_path), monkeypatch)


@pytest.fixture
def d(tmp_path: Any) -> Detached:
    """The bench of a runner that runs apart, with the double of Claude Code on its PATH."""
    return overnight_bench.detached(str(tmp_path))


def runner_attached(_: Any, monkeypatch: Any) -> None:
    """The runner starts as a child of the stacking session, which stops it as it ends."""
    monkeypatch.setenv(ATTACHED, "1")


def nothing_allowed(_: Any, monkeypatch: Any) -> None:
    """A session runs its prompt with no tool allowed and no mode, so each use waits for an
    approval that no one gives."""
    from session import permissions

    def arguments(task: Any, session: Any, prompt: str) -> list[str]:
        resumed = ["--resume", session] if session else []
        return ["-p", prompt, "--output-format", "stream-json", "--verbose", *resumed]

    monkeypatch.setattr(permissions, "arguments", arguments)


def everything_allowed(_: Any, monkeypatch: Any) -> None:
    """A session runs with every permission check bypassed, whatever the queue lets its task do."""
    from session import permissions

    given = permissions.arguments

    def arguments(task: Any, session: Any, prompt: str) -> list[str]:
        return [*given(task, session, prompt), "--dangerously-skip-permissions"]

    monkeypatch.setattr(permissions, "arguments", arguments)


def no_admission(_: Any, monkeypatch: Any) -> None:
    """A queue is taken in whatever keeps its tasks from starting."""
    from stacker import admission

    monkeypatch.setattr(admission, "faults", lambda queue, standing, sandbox_holds: ())


def queue_of_one_apart(_: Any, monkeypatch: Any) -> None:
    """A queue of one has a way of its own, which the commands and the runner don't serve."""
    from stacker import queue_file

    given = queue_file.read

    def read(path: str) -> Any:
        queue = given(path)
        if len(queue.tasks) == 1:
            fault = queue_file.Fault("a queue of one task", "stack it with another task")
            raise queue_file.Refused((fault,))
        return queue

    monkeypatch.setattr(queue_file, "read", read)


def resumed_at_the_reset(_: Any, monkeypatch: Any) -> None:
    """A task stopped by the limit goes on at the reset itself."""
    from runner import limit

    monkeypatch.setattr(limit, "resume_at", lambda reset, stops: None if stops >= 7 else reset)


def never_given_up(_: Any, monkeypatch: Any) -> None:
    """A task stopped by the limit goes on however many times it stopped."""
    from runner import limit

    monkeypatch.setattr(limit, "resume_at", lambda reset, stops: reset + timedelta(minutes=2))


def failed_read_as_finished(_: Any, monkeypatch: Any) -> None:
    """A session that ended without its answer reads as finished."""
    from session import ending

    given = ending.ending

    def read(output: Any, now: Any) -> Any:
        ended = given(output, now)
        if isinstance(ended, ending.Failed):
            return ending.Finished(ended.reply, ended.session or "")
        return ended

    monkeypatch.setattr(ending, "ending", read)


def one_fault_escapes(_: Any, monkeypatch: Any) -> None:
    """A fault met while carrying the review of the payments escapes its task to the runner."""
    from runner import task

    given = task.carry

    def carry(queue_file: str, carried: Any) -> None:
        if carried.task.name == "review-payments":
            raise RuntimeError("an error of the record")
        given(queue_file, carried)

    monkeypatch.setattr(task, "carry", carry)


def stop_unseen(_: Any, monkeypatch: Any) -> None:
    """A run whose runner stopped is left as it was."""
    from record import stopped

    monkeypatch.setattr(stopped, "left", lambda run, now: run)


def carried_on_anew(_: Any, monkeypatch: Any) -> None:
    """Each task of a queue stacked again starts anew, the finished ones among them."""
    from record import runs, stopped

    def carried_on(run: Any) -> Any:
        return runs.Run("waiting for the start", None, 0, (), None, None, None)

    monkeypatch.setattr(stopped, "carried_on", carried_on)


def four_at_a_time(_: Any, monkeypatch: Any) -> None:
    """Four tasks run at a time."""
    from runner import schedule

    monkeypatch.setattr(schedule, "AT_A_TIME", 4)


def wait_unsaid(_: Any, monkeypatch: Any) -> None:
    """A reply's part after a wait is added with no line saying when the limit stopped the task."""
    from record import replies

    monkeypatch.setattr(replies, "part", lambda reply, wait: reply.text)


def kept_elsewhere(b: Any, monkeypatch: Any) -> None:
    """What overnight writes for a queue lies in a folder of the user's home, apart from the queue
    file."""
    from record import place

    def of(queue_file: str) -> Any:
        folder = os.path.join(
            b.home, "elsewhere", os.path.splitext(os.path.basename(queue_file))[0]
        )
        return place.Place(
            folder, os.path.join(folder, "runs.json"), os.path.join(folder, "runner.lock")
        )

    monkeypatch.setattr(place, "of", of)


def worked_in_a_copy(b: Any, monkeypatch: Any) -> None:
    """A task's session works in a copy of its dir, which overnight leaves apart from it."""
    from session import session

    given = session.run

    def run(task: Any, session_id: Any) -> Any:
        copy = os.path.join(b.home, "copies", task.name)
        if not os.path.exists(copy):
            shutil.copytree(task.dir, copy)
        return given(dataclasses.replace(task, dir=copy), session_id)

    monkeypatch.setattr(session, "run", run)


BREAKS: dict[str, Callable[[Any, Any], None]] = {
    "test_the_tasks_go_on_after_the_stacking_session_ends": runner_attached,
    "test_a_task_uses_its_tools_with_no_permission_asked": nothing_allowed,
    "test_a_task_writes_only_where_the_queue_lets_it": everything_allowed,
    "test_a_queue_with_one_task_that_cant_start_runs_no_task": no_admission,
    "test_a_queue_of_one_waits_and_ends_as_any_queue": queue_of_one_apart,
    "test_a_task_stopped_by_the_limit_goes_on_in_its_session_two_minutes_after_the_reset": (
        resumed_at_the_reset
    ),
    "test_the_seventh_stop_at_the_limit_gives_the_task_up_with_why_and_its_session": (
        never_given_up
    ),
    "test_each_task_ends_finished_or_given_up_with_why_and_its_session": failed_read_as_finished,
    "test_a_task_given_up_stops_no_other_task": one_fault_escapes,
    "test_a_task_left_unended_by_a_stop_ends_given_up_with_that_reason": stop_unseen,
    "test_stacking_again_carries_on_each_unfinished_task_in_its_session": carried_on_anew,
    "test_the_tasks_start_at_the_start_three_at_a_time_in_the_queues_order": four_at_a_time,
    "test_a_resumed_tasks_reply_follows_its_earlier_one_with_the_wait": wait_unsaid,
    "test_each_task_and_reply_lies_beside_the_queue_file_for_a_later_session": kept_elsewhere,
    "test_what_a_task_writes_stays_in_its_dir_as_written": worked_in_a_copy,
}


@pytest.fixture
def broken(request: Any, monkeypatch: Any) -> None:
    """Takes out the part that holds the case's principle item where TRACE_BROKEN is 1, after the
    case's bench is set up; does nothing otherwise."""
    if os.environ.get("TRACE_BROKEN") != "1":
        return
    names = request.fixturenames
    bench = request.getfixturevalue("b") if "b" in names else request.getfixturevalue("d")
    BREAKS[request.node.originalname](bench, monkeypatch)
