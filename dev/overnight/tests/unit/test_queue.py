"""The unit cases of the queue, as the README's Walkthrough and How it works say: the works that
wait in it, in the order they were added, and the one runner that carries them one after another,
run in the test's own process with a double of `claude` and a clock that each wait moves on."""

from __future__ import annotations

import os

import pytest
from double.claude_double import DONE, RATE_LIMIT, RESUMED, Host, session_of
from double.clock import Clock
from overnight import queue, work

CLAUDE = ["claude", "-p", "--output-format", "json", "--allowed-tools", "Read"]
SHOP = "Move the tests to pytest"
BLOG = "Fix the broken links"


class Stopped(Exception):
    """The runner's stop, as a restart of the computer stops it, raised where a case stops it."""


def _stop(_: float) -> None:
    raise Stopped


def _dirs(tmp_path) -> tuple[str, str, str]:
    """The folder of the works, and the folders that the shop's and the blog's works run in."""
    for name in ("shop", "blog"):
        (tmp_path / name).mkdir()
    return str(tmp_path / "works"), str(tmp_path / "shop"), str(tmp_path / "blog")


def _add(top: str, clock: Clock, where: str, prompt: str, retries: int = 7) -> str:
    """Adds the work a minute after the last one, as the user types the next command."""
    folder = queue.add(top, work.Work(where, "Read", retries, prompt), clock.now, clock.sleep)
    clock.sleep(60)
    return folder


def test_no_work_is_pending_where_none_was_added(tmp_path):
    """Given no work added, and so no folder of the works
    When overnight asks for the works pending
    Then there are none"""
    assert queue.pending(str(tmp_path / "works")) == []


def test_a_work_added_waits_in_a_folder_named_by_the_time_it_was_added(tmp_path):
    """Given no work added
    When the user adds a work at 23:15:00
    Then its folder is 20261128-231500 in the folder of the works, and the work waits"""
    top, shop, _ = _dirs(tmp_path)
    folder = _add(top, Clock(), shop, SHOP)
    assert folder == os.path.join(top, "20261128-231500")
    assert work.status(folder) == "waiting"


def test_a_work_added_in_the_same_second_as_another_takes_the_next_second(tmp_path):
    """Given a work added at 23:15:00
    When the user adds another in the same second
    Then overnight waits a second, and names the other's folder 20261128-231501"""
    top, shop, blog = _dirs(tmp_path)
    clock = Clock()
    queue.add(top, work.Work(shop, "Read", 7, SHOP), clock.now, clock.sleep)
    folder = queue.add(top, work.Work(blog, "Read", 7, BLOG), clock.now, clock.sleep)
    assert (os.path.basename(folder), clock.waits) == ("20261128-231501", [1])


def test_the_works_pending_are_in_the_order_they_were_added(tmp_path):
    """Given the shop's work added, then the blog's
    When overnight asks for the works pending
    Then they are the shop's work, then the blog's"""
    top, shop, blog = _dirs(tmp_path)
    clock = Clock()
    first = _add(top, clock, shop, SHOP)
    second = _add(top, clock, blog, BLOG)
    assert queue.pending(top) == [first, second]


def test_the_runner_carries_the_works_one_after_another_in_the_order_they_were_added(tmp_path):
    """Given the shop's work added, then the blog's, and `claude`, whose runs are done
    When the runner runs
    Then it runs the shop's work, then the blog's, records each done, and leaves none pending"""
    top, shop, blog = _dirs(tmp_path)
    clock = Clock()
    first = _add(top, clock, shop, SHOP)
    second = _add(top, clock, blog, BLOG)
    host = Host(DONE, DONE)
    queue.run(top, host, clock.now, clock.sleep)
    assert host.calls == [(CLAUDE, shop, SHOP), (CLAUDE, blog, BLOG)]
    assert (work.status(first), work.status(second), queue.pending(top)) == ("done", "done", [])


def test_a_work_whose_retries_run_out_lets_the_next_work_run(tmp_path):
    """Given the shop's work, with 0 retries, whose run the rate limit stops, then the blog's work
    When the runner runs
    Then it records the shop's work failed, and runs the blog's work after it"""
    top, shop, blog = _dirs(tmp_path)
    clock = Clock()
    first = _add(top, clock, shop, SHOP, retries=0)
    second = _add(top, clock, blog, BLOG)
    host = Host(RATE_LIMIT, DONE)
    queue.run(top, host, clock.now, clock.sleep)
    assert host.calls == [(CLAUDE, shop, SHOP), (CLAUDE, blog, BLOG)]
    assert (work.status(first), work.status(second)) == ("failed", "done")


def test_a_work_that_runs_is_pending_with_those_that_wait(tmp_path):
    """Given the shop's work, whose run the rate limit stops, then the blog's work
    When overnight asks for the works pending as the shop's work waits for its retry
    Then they are the shop's work, then the blog's"""
    top, shop, blog = _dirs(tmp_path)
    clock = Clock()
    first = _add(top, clock, shop, SHOP)
    second = _add(top, clock, blog, BLOG)
    seen: list[list[str]] = []

    def sleep(seconds: float) -> None:
        seen.append(queue.pending(top))
        clock.sleep(seconds)

    queue.run(top, Host(RATE_LIMIT, RESUMED, DONE), clock.now, sleep)
    assert seen == [[first, second]]


def test_a_work_added_while_the_runner_runs_joins_the_queue(tmp_path):
    """Given the shop's work, whose first run the rate limit stops
    When the user adds the blog's work as the shop's work waits for its retry
    Then the runner runs the blog's work once the shop's work is done"""
    top, shop, blog = _dirs(tmp_path)
    clock = Clock()
    _add(top, clock, shop, SHOP)
    added: list[str] = []

    def sleep(seconds: float) -> None:
        added.append(_add(top, clock, blog, BLOG))
        clock.sleep(seconds)

    host = Host(RATE_LIMIT, RESUMED, DONE)
    queue.run(top, host, clock.now, sleep)
    resume = [*CLAUDE, "--resume", session_of(RATE_LIMIT)]
    assert host.calls == [(CLAUDE, shop, SHOP), (resume, shop, "continue"), (CLAUDE, blog, BLOG)]
    assert work.status(added[0]) == "done"


def test_a_work_added_just_as_the_runner_ends_still_runs(tmp_path, monkeypatch):
    """Given the shop's work, and a runner that has carried it and found no work left
    When the user adds the blog's work before that runner lets go of the queue, so that the runner
    that the add starts finds one still running and runs nothing
    Then the first runner runs the blog's work before it ends"""
    top, shop, blog = _dirs(tmp_path)
    clock = Clock()
    _add(top, clock, shop, SHOP)
    looks = queue.pending
    added: list[str] = []
    second = Host()

    # The moment between the runner's last look and its end has no hook, so the user's add comes
    # in on the look that first finds no work left.
    def pending(folder: str) -> list[str]:
        found = looks(folder)
        if not found and not added:
            added.append(_add(top, clock, blog, BLOG))
            queue.run(top, second, clock.now, clock.sleep)
        return found

    monkeypatch.setattr(queue, "pending", pending)
    host = Host(DONE, DONE)
    queue.run(top, host, clock.now, clock.sleep)
    assert host.calls == [(CLAUDE, shop, SHOP), (CLAUDE, blog, BLOG)]
    assert (second.calls, work.status(added[0])) == ([], "done")


def test_a_second_runner_runs_nothing_while_one_runs(tmp_path):
    """Given the shop's work, whose first run the rate limit stops, then the blog's work
    When a second runner runs as the first runner waits for the shop's retry
    Then the second runs no work, and the first carries both"""
    top, shop, blog = _dirs(tmp_path)
    clock = Clock()
    _add(top, clock, shop, SHOP)
    _add(top, clock, blog, BLOG)
    second = Host(DONE)

    def sleep(seconds: float) -> None:
        queue.run(top, second, clock.now, clock.sleep)
        clock.sleep(seconds)

    first = Host(RATE_LIMIT, RESUMED, DONE)
    queue.run(top, first, clock.now, sleep)
    resume = [*CLAUDE, "--resume", session_of(RATE_LIMIT)]
    assert first.calls == [(CLAUDE, shop, SHOP), (resume, shop, "continue"), (CLAUDE, blog, BLOG)]
    assert second.calls == []


def test_a_runner_started_again_goes_on_with_the_work_that_was_running(tmp_path):
    """Given the shop's work, whose first run the rate limit stops, then the blog's work, and a
    runner that stopped as the shop's work waited for its retry
    When the runner runs again
    Then it asks `claude` to continue in the shop's session, then runs the blog's work"""
    top, shop, blog = _dirs(tmp_path)
    clock = Clock()
    first = _add(top, clock, shop, SHOP)
    second = _add(top, clock, blog, BLOG)
    with pytest.raises(Stopped):
        queue.run(top, Host(RATE_LIMIT), clock.now, _stop)
    host = Host(RESUMED, DONE)
    queue.run(top, host, clock.now, clock.sleep)
    resume = [*CLAUDE, "--resume", session_of(RATE_LIMIT)]
    assert host.calls == [(resume, shop, "continue"), (CLAUDE, blog, BLOG)]
    assert (work.status(first), work.status(second)) == ("done", "done")


def test_a_runner_started_again_runs_no_work_that_ended(tmp_path):
    """Given the shop's work and the blog's, which a runner carried until both were done
    When the runner runs again
    Then it runs no work"""
    top, shop, blog = _dirs(tmp_path)
    clock = Clock()
    _add(top, clock, shop, SHOP)
    _add(top, clock, blog, BLOG)
    queue.run(top, Host(DONE, DONE), clock.now, clock.sleep)
    again = Host()
    queue.run(top, again, clock.now, clock.sleep)
    assert again.calls == []
