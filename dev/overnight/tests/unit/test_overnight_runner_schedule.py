"""The unit cases of runner/schedule.py, when each task of a queue starts: `carry`, of a queue with
no start, of one whose start comes later that day, at that minute, and has passed that day, of
none, one, three, and five tasks, each carried by a stand-in for `runner.task.carry` that takes a
while, of five whose first stays at work long after the others end, as a task that waits hours at
the usage limit does, and of a queue that another runner holds."""

from __future__ import annotations

import threading
import time
from typing import Any

import pytest
from overnight_bench import START, Bench, at, bench, held_elsewhere, walkthrough
from record import lock, place
from runner import schedule, task
from runner.handoff import Carried, Handoff
from stacker.queue_file import Task

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


class Carrier:
    """A stand-in for `runner.task.carry` that keeps each task it carried, when on the clock, and
    how many were carried at once at most, each taking the seconds. The task named `held` stays at
    work until each task of `until` has started, ten seconds at most, and keeps in `saw` whether
    they started while it was at work."""

    def __init__(
        self, b: Bench, seconds: float, held: str | None = None, until: tuple[str, ...] = ()
    ):
        self.b = b
        self.seconds = seconds
        self.held = held
        self.until = set(until)
        self.saw = False
        self.carried: list[tuple[str, Any]] = []
        self.now = 0
        self.most = 0
        self._lock = threading.Condition()

    def __call__(self, queue_file: str, carried: Carried) -> None:
        name = carried.task.name
        with self._lock:
            self.carried.append((name, self.b.clock.now()))
            self.now += 1
            self.most = max(self.most, self.now)
            self._lock.notify_all()
            if name == self.held:
                self.saw = self._lock.wait_for(
                    lambda: self.until <= {each for each, _ in self.carried}, timeout=10
                )
        time.sleep(self.seconds)
        with self._lock:
            self.now -= 1


def queue_of(b: Bench, names: list[str], start: str | None) -> Handoff:
    """A handoff of a queue of tasks of the names, each anew, with the start."""
    tasks = tuple(
        Carried(Task(name, b.path("overnight", f"{name}.md"), b.path("work", "shop"), False), None)
        for name in names
    )
    return Handoff(b.queue_file, start, tasks)


def carrier(b: Bench, monkeypatch: Any, seconds: float = 0.0, **held: Any) -> Carrier:
    the = Carrier(b, seconds, **held)
    monkeypatch.setattr(task, "carry", the)
    return the


def bench_at(tmp_path: Any, monkeypatch: Any, start: Any) -> Bench:
    the = bench(str(tmp_path), monkeypatch, start)
    walkthrough(the)
    return the


@pytest.mark.supports("test_a_queue_without_start_starts_its_tasks_at_once")
def test_a_queue_with_no_start_carries_its_tasks_at_once(tmp_path: Any, monkeypatch: Any):
    """Given a queue of one task with no start, at 22:30
    When it is carried
    Then no wait comes, and the task is carried at 22:30"""
    b = bench_at(tmp_path, monkeypatch, at(22, 30))
    carried = carrier(b, monkeypatch)

    schedule.carry(queue_of(b, ["a"], None))

    assert b.clock.waits == []
    assert carried.carried == [("a", at(22, 30))]


@pytest.mark.supports("test_a_queue_stacked_anew_waits_for_its_start")
def test_a_start_later_that_day_is_waited_for(tmp_path: Any, monkeypatch: Any):
    """Given a queue from 23:00 of one task, at 22:59
    When it is carried
    Then it waits until 23:00 that day, and carries the task then"""
    b = bench_at(tmp_path, monkeypatch, at(22, 59))
    carried = carrier(b, monkeypatch)

    schedule.carry(queue_of(b, ["a"], "23:00"))

    assert b.clock.waits == [START]
    assert carried.carried == [("a", START)]


@pytest.mark.supports("test_a_queue_stacked_anew_waits_for_its_start")
def test_a_start_at_its_minute_carries_the_tasks_then(tmp_path: Any, monkeypatch: Any):
    """Given a queue from 23:00 of one task, at 23:00
    When it is carried
    Then it carries the task at 23:00, waiting no longer"""
    b = bench_at(tmp_path, monkeypatch, START)
    carried = carrier(b, monkeypatch)

    schedule.carry(queue_of(b, ["a"], "23:00"))

    assert b.clock.waits in ([], [START])
    assert carried.carried == [("a", START)]


@pytest.mark.supports("test_a_queue_stacked_after_its_start_hour_waits_for_it_the_next_day")
def test_a_start_passed_that_day_is_waited_for_the_next_day(tmp_path: Any, monkeypatch: Any):
    """Given a queue from 23:00 of one task, at 23:01
    When it is carried
    Then it waits until 23:00 of the next day, and carries the task then"""
    b = bench_at(tmp_path, monkeypatch, at(23, 1))
    carried = carrier(b, monkeypatch)

    schedule.carry(queue_of(b, ["a"], "23:00"))

    assert b.clock.waits == [at(23, 0, 1)]
    assert carried.carried == [("a", at(23, 0, 1))]


@pytest.mark.supports("test_a_queue_without_start_starts_its_tasks_at_once")
def test_a_queue_of_no_task_carries_none_and_lets_its_lock_go(tmp_path: Any, monkeypatch: Any):
    """Given a queue of no task with no start
    When it is carried
    Then it carries none, and no program holds the queue's lock afterward"""
    b = bench_at(tmp_path, monkeypatch, at(22, 30))
    carried = carrier(b, monkeypatch)

    schedule.carry(queue_of(b, [], None))

    assert carried.carried == []
    assert not lock.held(place.of(b.queue_file).lock)


@pytest.mark.supports("test_the_tasks_start_at_the_start_three_at_a_time_in_the_queues_order")
@pytest.mark.parametrize(("count", "most"), [(1, 1), (3, 3), (5, 3)])
def test_tasks_are_carried_three_at_a_time_in_the_queues_order(
    tmp_path: Any, monkeypatch: Any, count: int, most: int
):
    """Given a queue of one, three, or five tasks with no start, named last first, each of which
    takes a third of a second
    When it is carried
    Then each is carried once, at most three at once, the first three before any other, and the
    fourth and fifth in the queue's order"""
    b = bench_at(tmp_path, monkeypatch, at(22, 30))
    carried = carrier(b, monkeypatch, 0.3)
    names = ["e", "d", "c", "b", "a"][:count]

    schedule.carry(queue_of(b, names, None))

    order = [name for name, _ in carried.carried]
    assert sorted(order) == sorted(names)
    assert carried.most == most
    assert sorted(order[:3]) == sorted(names[:3])
    assert order[3:] == names[3:]


@pytest.mark.supports("test_the_tasks_start_at_the_start_three_at_a_time_in_the_queues_order")
def test_a_task_that_stays_at_work_leaves_the_others_to_go_on_beside_it(
    tmp_path: Any, monkeypatch: Any
):
    """Given a queue of five tasks with no start, whose first stays at work until the fourth and
    fifth have started, as a task that waits hours at the usage limit does, and whose others end
    at once
    When it is carried
    Then the fourth and fifth start while the first is still at work, each is carried once, at
    most three at once, and the fourth and fifth in the queue's order"""
    b = bench_at(tmp_path, monkeypatch, at(22, 30))
    names = ["a", "b", "c", "d", "e"]
    carried = carrier(b, monkeypatch, held="a", until=("d", "e"))

    schedule.carry(queue_of(b, names, None))

    order = [name for name, _ in carried.carried]
    assert carried.saw
    assert sorted(order) == names
    assert carried.most == 3
    assert order[3:] == ["d", "e"]


@pytest.mark.supports("test_a_runner_started_on_a_queue_that_another_runner_carries_runs_no_task")
def test_a_queue_that_another_runner_holds_is_refused_carrying_none(
    tmp_path: Any, monkeypatch: Any
):
    """Given a queue of one task with no start, whose lock another runner holds
    When it is carried
    Then it refuses with Held, and carries none"""
    b = bench_at(tmp_path, monkeypatch, at(22, 30))
    carried = carrier(b, monkeypatch)

    with held_elsewhere(b.queue_file), pytest.raises(lock.Held):
        schedule.carry(queue_of(b, ["a"], None))

    assert carried.carried == []
