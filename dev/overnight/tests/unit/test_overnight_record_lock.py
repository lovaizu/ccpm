"""The unit cases of record/lock.py, how a runner's stop shows: `hold`, where no lock's file is
there, where another program holds the lock, and after the program that held it was killed; and
`held`, with no lock's file, with one that no program holds, with one another program holds, and
after one asks, so that asking takes no lock."""

from __future__ import annotations

import os
import subprocess
import sys
from contextlib import AbstractContextManager
from typing import Any

import pytest
from overnight_bench import DOMAIN, end_group, held_by_another
from record.lock import Held, held, hold

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


def another(path: str) -> AbstractContextManager[subprocess.Popen[str]]:
    """Another program holding the lock at the path until the block ends or it is killed."""
    return held_by_another(f"lock.hold({path!r})")


def asked_elsewhere(path: str) -> bool:
    """Whether another program, such as the stacker or the checker, finds the lock held."""
    code = f"import sys\nsys.path.insert(0, {DOMAIN!r})\nfrom record import lock\n"
    code += f"print(lock.held({path!r}))\n"
    done = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    return done.stdout == "True\n"


@pytest.mark.supports(
    "test_a_queue_whose_runner_still_carries_it_is_refused_with_where_its_tasks_stand",
    "test_a_runner_started_on_a_queue_that_another_runner_carries_runs_no_task",
)
def test_a_lock_with_no_file_is_held_and_made(tmp_path: Any):
    """Given a queue's folder with no lock's file
    When the lock is held
    Then its file is there, another program finds it held while the block runs, and none after"""
    path = os.path.join(str(tmp_path), "runner.lock")

    with hold(path):
        assert os.path.exists(path)
        assert asked_elsewhere(path)

    assert not asked_elsewhere(path)
    assert not held(path)


@pytest.mark.supports(
    "test_a_queue_whose_runner_still_carries_it_is_refused_with_where_its_tasks_stand",
    "test_a_runner_started_on_a_queue_that_another_runner_carries_runs_no_task",
)
def test_a_lock_another_program_holds_is_refused(tmp_path: Any):
    """Given a lock that another program holds
    When it is held
    Then it refuses with Held, and the other program still holds it"""
    path = os.path.join(str(tmp_path), "runner.lock")

    with another(path):
        with pytest.raises(Held), hold(path):
            pass
        assert held(path)


@pytest.mark.supports("test_a_runner_killed_mid_task_leaves_the_task_given_up_at_the_next_check")
def test_a_lock_whose_program_was_killed_is_held_by_none(tmp_path: Any):
    """Given a lock that another program held when it was killed with no time to let it go
    When it is asked whether a program holds it, and then held
    Then none holds it, and it is held"""
    path = os.path.join(str(tmp_path), "runner.lock")

    with another(path) as holder:
        end_group(holder.pid)
        holder.wait(timeout=30)

    assert not held(path)
    with hold(path):
        assert asked_elsewhere(path)


@pytest.mark.supports(
    "test_a_queue_whose_runner_still_carries_it_is_refused_with_where_its_tasks_stand"
)
def test_no_lock_file_is_held_by_none(tmp_path: Any):
    """Given a queue's folder with no lock's file
    When it is asked whether a program holds the lock
    Then none does, and no lock's file is made"""
    path = os.path.join(str(tmp_path), "runner.lock")

    assert not held(path)
    assert not os.path.exists(path)


@pytest.mark.supports(
    "test_a_queue_whose_runner_still_carries_it_is_refused_with_where_its_tasks_stand"
)
def test_asking_takes_no_lock(tmp_path: Any):
    """Given a lock's file that no program holds
    When it is asked whether a program holds it, and then another program holds it
    Then none held it, and the other program holds it"""
    path = os.path.join(str(tmp_path), "runner.lock")
    with hold(path):
        pass

    assert not held(path)
    with another(path):
        assert held(path)
