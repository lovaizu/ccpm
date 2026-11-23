"""The unit cases of stacker/detach.py, how a queue's runner outlives the session that starts it:
`start_runner`, of a queue whose task takes long, which it starts and doesn't wait for, handing the
runner the queue on its standard input, and of an OS that doesn't start it."""

from __future__ import annotations

import subprocess
import time
from typing import Any

import claude_double
import pytest
from overnight_bench import Detached, detached, stacked_review, until
from record import store
from stacker.detach import CantStart, start_runner

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


@pytest.fixture
def d(tmp_path: Any, monkeypatch: Any) -> Detached:
    the = detached(str(tmp_path))
    monkeypatch.setenv("PATH", the.env()["PATH"])
    return the


@pytest.mark.supports("test_the_tasks_go_on_after_the_stacking_session_ends")
def test_the_runner_starts_apart_and_the_stacker_goes_on_at_once(d: Detached):
    """Given a stacked queue of one review whose session takes three seconds
    When its runner is started
    Then the start returns within one second, the runner runs the review in its folder, and the
    review is finished afterward"""
    given = stacked_review(d, 3)
    began = time.monotonic()

    start_runner(given)

    assert time.monotonic() - began < 1
    assert until(lambda: len(claude_double.asked(d.claude)) == 1, 30)
    assert claude_double.asked(d.claude)[0].cwd == d.path("work")
    assert until(lambda: store.standing(given.queue_file).tasks[0].run.state == "finished", 30)


@pytest.mark.supports("test_the_tasks_go_on_after_the_stacking_session_ends")
def test_a_runner_the_os_doesnt_start_is_refused_with_what_it_said(d: Detached, monkeypatch: Any):
    """Given a stacked queue of one review, on a computer that refuses to start a program
    When its runner is started
    Then it refuses with CantStart, with what the OS said"""
    given = stacked_review(d, 0)

    def refused(*args: Any, **kwargs: Any) -> Any:
        raise OSError(11, "Resource temporarily unavailable")

    monkeypatch.setattr(subprocess, "Popen", refused)

    with pytest.raises(CantStart, match="Resource temporarily unavailable"):
        start_runner(given)
