"""Decides the queue: where the works wait, in what order, and that one runner at a time carries
them, one after another."""

from __future__ import annotations

import datetime
import fcntl
import os
import subprocess
import sys
from typing import Callable

from overnight import claude, work

# The package that runs the queue apart from the session, as `start` runs it.
RUNNER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runner")
# The file in the folder of the works that the runner holds locked as it runs, so that no second
# runner runs, and that the system frees as the runner stops, however it stops.
LOCK = "runner.lock"
# What the runner writes on stdout and stderr, such as a traceback, in the folder of the works.
RUNNER_LOG = "runner.log"


def pending(top: str) -> list[str]:
    """The folders of the works in the folder of the works that haven't ended, the one running and
    those waiting, in the order they were added, or [] where the folder doesn't exist."""
    if not os.path.isdir(top):
        return []
    folders = [os.path.join(top, name) for name in sorted(os.listdir(top))]
    return [each for each in folders if work.status(each) in ("waiting", "running")]


def add(
    top: str,
    added: work.Work,
    now: Callable[[], datetime.datetime],
    sleep: Callable[[float], None],
) -> str:
    """Adds the work to the end of the queue, and gives the folder where it waits.

    Takes: the folder of the works, which `add` makes where it doesn't exist, the work, the clock
    that gives the local time, and the sleep that waits for a number of seconds.
    Gives: `<top>/<yyyymmdd-hhmmss>`, named by the time of the add, so that the names sort in the
    order the works were added. Where another work holds that name, it waits a second and takes
    the next.
    """
    os.makedirs(top, exist_ok=True)
    # A second passes after each try that finds the name taken, so a free name comes.
    while True:
        folder = os.path.join(top, f"{now():%Y%m%d-%H%M%S}")
        try:
            os.mkdir(folder)
            break
        except FileExistsError:
            sleep(1)
    work.put(folder, added)
    return folder


def start(top: str) -> None:
    """Starts the runner apart from the caller's session, and returns at once.

    Takes: the folder of the works, which exists.
    Changes: starts `python3 <scripts>/runner <top>` in a session of its own, so that closing the
    caller's session doesn't stop it, with what it writes, such as a traceback, appended to
    `<top>/runner.log`. Where a runner already runs, the new one ends at once, as `run` says.
    """
    with open(os.path.join(top, RUNNER_LOG), "a", encoding="utf-8") as log:
        subprocess.Popen(
            [sys.executable, RUNNER, top],
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
            start_new_session=True,
        )


def run(
    top: str,
    host: claude.Host,
    now: Callable[[], datetime.datetime],
    sleep: Callable[[float], None],
) -> None:
    """Runs the queue: carries each pending work in turn, as `work.carry` says, until none is
    pending, the one that was running first, so that a runner started again goes on with it.

    Takes: the folder of the works, which exists, the host that runs `claude`, the clock, and the
    sleep, as `work.carry` takes them.
    Changes: carries the works, and returns once none is pending. A work whose carry raises an
    error that its folders cause, such as one whose `dir` is gone, is failed, as `work.fail` says,
    and the next is carried. Where another runner runs, it returns at once and carries nothing.
    """
    # The lock is freed before the last look, so a work added as the runner ends is either seen by
    # that look or added after the lock is free, for the runner that its add starts.
    while pending(top):
        with open(os.path.join(top, LOCK), "a", encoding="utf-8") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return
            folders = pending(top)
            while folders:
                # The errors that a work's own folders cause, such as a `dir` that is gone or a
                # file of the work that isn't JSON, fail that work alone and leave the rest of the
                # night to the next. Any other error stops the runner, and leaves the work running
                # for the runner started again.
                try:
                    work.carry(folders[0], host, now, sleep)
                except (OSError, ValueError) as error:
                    work.fail(folders[0], now(), error)
                folders = pending(top)
