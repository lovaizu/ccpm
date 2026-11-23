"""The property-based tests of the runner, as overnight's Test strategy names them: the runner
starts with what the stacker hands it alone, as P1.1 says, so any handoff reads back as it was
given (model-based, of Task); a task stopped by the limit goes on two minutes after the reset and
is given up at its seventh stop, as P2.1 and P2.2 say (model-based); every task ends, finished
or given up with why and its session, whatever its sessions meet, as P3.1 says (model-based); and a
queue's tasks run three at a time in the queue's order, each end starting the next, and each ends
as its own sessions say, however the others end, as P4.1 and P3.2 say (model-based)."""

from __future__ import annotations

import os
import tempfile
import threading
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any

import claude_double
import pytest
from claude_double import Answer
from hypothesis import given, settings
from hypothesis import strategies as st
from overnight_bench import PAYMENTS_PROMPT, bench, one_review, walkthrough
from overnight_generators import LOCAL_MOMENTS, MOMENTS, NAMES, WORDS
from record import store
from runner import schedule, task
from runner.handoff import Carried, Handoff, decode, encode
from runner.limit import resume_at
from runner.task import carry
from stacker import queue_file
from stacker.queue_file import Task

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")

PATHS = st.lists(WORDS, min_size=1, max_size=3).map(lambda words: os.path.join(os.sep, *words))
CARRIED = st.builds(
    lambda name, prompt, folder, writes, session: Carried(
        Task(name, prompt, folder, writes), session
    ),
    NAMES,
    PATHS,
    PATHS,
    st.booleans(),
    st.none() | st.uuids().map(str),
)
HOURS = st.none() | st.builds(
    lambda h, m: f"{h:02d}:{m:02d}", st.integers(0, 23), st.integers(0, 59)
)


@pytest.mark.supports("test_the_tasks_go_on_after_the_stacking_session_ends")
@given(PATHS, HOURS, st.lists(CARRIED, max_size=5))
def test_any_handoff_reads_back_as_the_stacker_gave_it(path: str, start, tasks: list[Carried]):
    """Given any queue file, any start or none, and any tasks, each anew or in its session
    When the stacker's handoff is encoded and the runner decodes it
    Then the runner has the same queue file, start, and tasks, in their order"""
    given_handoff = Handoff(path + ".json", start, tuple(tasks))

    assert decode(encode(given_handoff)) == given_handoff


@pytest.mark.supports(
    "test_a_task_stopped_by_the_limit_goes_on_in_its_session_two_minutes_after_the_reset"
)
@given(MOMENTS, st.integers(1, 7))
def test_a_stop_at_the_limit_goes_on_two_minutes_after_the_reset_until_the_seventh(
    reset, stops: int
):
    """Given any moment the limit resets at, and any stop from the first to the seventh
    When when the task goes on is found
    Then it is two minutes after the reset before the seventh stop, and none at it"""
    expected = None if stops == 7 else reset + timedelta(minutes=2)

    assert resume_at(reset, stops) == expected


# How a run of a task's session ends, as Claude Code ends one: it answers, the limit stops it, or
# it fails.
ENDS = st.sampled_from(["finished", "limited", "failed"])


def answers_of(ends: list[str], start: datetime) -> list[Answer]:
    """The runs of a task's sessions, each ending as `ends` says, half an hour apart from the
    moment, each stop at the limit reset fifty minutes after it, and a last run that finishes."""
    answers, moment = [], start
    for end in ends + ["finished"]:
        moment += timedelta(minutes=30)
        reset = moment + timedelta(minutes=50)
        answers.append(
            Answer(end, f"part {len(answers)}", moment, reset if end == "limited" else None)
        )
        if end == "limited":
            moment = reset + timedelta(minutes=2)
    return answers


def ended_as(ends: list[str]) -> tuple[str, int, bool]:
    """How a task whose sessions end as `ends` says, and then finish, ends, as P2.2 and P3.1 say:
    its state, its stops at the limit, and whether it says why."""
    stops = 0
    for end in ends + ["finished"]:
        if end == "limited":
            stops += 1
            if stops == 7:
                return "given up", stops, True
            continue
        return ("given up", stops, True) if end == "failed" else ("finished", stops, False)
    raise AssertionError("a task's last session finishes")


@pytest.mark.supports("test_each_task_ends_finished_or_given_up_with_why_and_its_session")
@given(st.lists(ENDS, min_size=1, max_size=9), LOCAL_MOMENTS)
def test_every_task_ends_finished_or_given_up_with_why_and_its_session(ends: list[str], start):
    """Given a task whose sessions end in any order of finishing, stops at the limit, and failures,
    the last of them finishing where none ends it before, from any moment
    When it is carried
    Then it is finished where a session finished before a failure and before the seventh stop,
    and given up with why otherwise, each in its first session, with its stops counted"""
    with tempfile.TemporaryDirectory() as top, pytest.MonkeyPatch.context() as monkeypatch:
        b = bench(top, monkeypatch, start)
        walkthrough(b)
        one_review(b)
        claude_double.script(b.claude, PAYMENTS_PROMPT, *answers_of(ends, start))
        queue = queue_file.read(b.queue_file)
        store.stack(queue)

        carry(b.queue_file, Carried(queue.tasks[0], None))

        run = b.run_of("review-payments")
        sessions = {each.session for each in b.asked()}
    assert (run["state"], run["stops"], bool(run.get("why"))) == ended_as(ends)
    assert len(sessions) == 1 and run["session"] in sessions


class Gate:
    """A wrap of `runner.task.carry` that keeps each task at work until the case lets it go on, and
    then carries it as `runner.task.carry` does, so that the case decides the order in which the
    tasks end. It keeps the tasks at work, those ended, and the most at work at once."""

    def __init__(self, real: Callable[[str, Carried], None]):
        self.real = real
        self.at_work: list[str] = []
        self.ended: list[str] = []
        self.let_go: set[str] = set()
        self.most = 0
        self.changed = threading.Condition()

    def __call__(self, queue_file: str, carried: Carried) -> None:
        name = carried.task.name
        with self.changed:
            self.at_work.append(name)
            self.most = max(self.most, len(self.at_work))
            self.changed.notify_all()
            self.changed.wait_for(lambda: name in self.let_go, timeout=30)
        try:
            self.real(queue_file, carried)
        finally:
            with self.changed:
                self.at_work.remove(name)
                self.ended.append(name)
                self.changed.notify_all()

    def go_on(self, name: str) -> None:
        """Lets the task go on to its end."""
        with self.changed:
            self.let_go.add(name)
            self.changed.notify_all()

    def wake(self) -> None:
        """Wakes each wait, as the runner's end changes what `settle` waits for."""
        with self.changed:
            self.changed.notify_all()

    def settle(self, at_work: list[str], ended: list[str], runner: Future[None]) -> None:
        """Waits, two seconds at most, until the tasks at work and those ended are the ones given,
        a task is at work that isn't one of them, or the runner has ended. Then it waits a moment
        more for a task at work that isn't one of them, as a runner that starts more than it may
        starts them together."""

        def extra() -> bool:
            return bool(set(self.at_work) - set(at_work) - set(ended)) or runner.done()

        def settled() -> bool:
            matches = (sorted(self.at_work), sorted(self.ended)) == (sorted(at_work), sorted(ended))
            return matches or extra()

        with self.changed:
            self.changed.wait_for(settled, timeout=2)
            self.changed.wait_for(extra, timeout=0.05)


@pytest.mark.supports(
    "test_the_tasks_start_at_the_start_three_at_a_time_in_the_queues_order",
    "test_a_task_given_up_stops_no_other_task",
)
# Fewer examples than the profile's, as each end of a task waits a moment for a start too many.
@settings(max_examples=40)
@given(st.lists(st.lists(ENDS, min_size=1, max_size=9), min_size=1, max_size=7), st.data())
def test_any_queue_runs_three_at_a_time_and_each_task_ends_however_the_others_end(
    tasks_ends: list[list[str]], data: Any
):
    """Given any queue of tasks with no start, each whose sessions end in any order of finishing,
    stops at the limit, and failures, the tasks ending one at a time in any order
    When its runner carries it
    Then the first three are at work at once, each end of a task starts the next in the queue's
    order while one waits, no more than three are at work at any time, the runner ends once each
    task has ended, and each task ends finished or given up with why, as its own sessions say"""
    names = [f"task-{i}" for i in range(len(tasks_ends))]
    prompts = {name: f"Review the module {name}/." for name in names}
    with tempfile.TemporaryDirectory() as top, pytest.MonkeyPatch.context() as monkeypatch:
        b = bench(top, monkeypatch)
        b.write(b.path("work", "shop", "README"), "")
        for name, ends in zip(names, tasks_ends):
            b.write(b.path("overnight", f"{name}.md"), prompts[name])
            claude_double.script(b.claude, prompts[name], *answers_of(ends, b.clock.now()))
        listed = [{"name": n, "prompt": f"{n}.md", "dir": b.path("work", "shop")} for n in names]
        b.queue({"tasks": listed})
        queue = queue_file.read(b.queue_file)
        store.stack(queue)
        gate = Gate(task.carry)
        monkeypatch.setattr(task, "carry", gate)
        handoff = Handoff(b.queue_file, None, tuple(Carried(each, None) for each in queue.tasks))
        pool = ThreadPoolExecutor(max_workers=1)
        runner = pool.submit(schedule.carry, handoff)
        runner.add_done_callback(lambda _: gate.wake())
        at_work, waiting, ended = names[:3], names[3:], []
        try:
            while at_work:
                gate.settle(at_work, ended, runner)
                if runner.done():
                    runner.result()
                assert (sorted(gate.at_work), sorted(gate.ended)) == (
                    sorted(at_work),
                    sorted(ended),
                )
                name = data.draw(st.sampled_from(sorted(at_work)))
                gate.go_on(name)
                at_work.remove(name)
                ended.append(name)
                if waiting:
                    at_work.append(waiting.pop(0))
        finally:
            for name in names:
                gate.go_on(name)
            pool.shutdown()

        runner.result(timeout=0)
        assert (sorted(gate.ended), gate.most) == (sorted(names), min(3, len(names)))
        for name, ends in zip(names, tasks_ends):
            run = b.run_of(name)
            sessions = {each.session for each in b.asked() if each.prompt == prompts[name]}
            assert (run["state"], run["stops"], bool(run.get("why"))) == ended_as(ends)
            assert len(sessions) == 1 and run["session"] in sessions
