"""Decides the course of one work: its runs of `claude`, the waits between them, when the work is
done or failed, and what its folder records of it, in `state.json` and `log`."""

from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys
from typing import Callable, NamedTuple

from overnight import claude

# The minutes to wait before each retry, the last for each retry after it. They grow so that a
# limit that holds gets few requests, and end at an hour so that the work goes on within an hour
# after the 5-hour limit lifts: 7 retries wait 275 minutes in all, which spans it.
WAITS = (5, 10, 20, 60)
# The retries of a work whose `--retries` the user doesn't give.
RETRIES = 7
# What a retry asks Claude, in the session where the run stopped, as the user would type it.
CONTINUE = "continue"
# The package that carries a work apart from the session, as `start` runs it.
CARRY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "carry")
# The work's log in its folder: the lines of its course, and what the process that carries it
# writes, such as a traceback.
LOG = "log"


class Work(NamedTuple):
    """One work: the folder Claude works in, the tools it may use, as `--allowed-tools` takes
    them, how many times a stopped run is retried, and the prompt."""

    dir: str
    tools: str
    retries: int
    prompt: str


def start(folder: str, work: Work) -> None:
    """Starts carrying the work apart from the caller's session, and returns at once.

    Takes: the work's folder, which exists, and the work.
    Changes: starts `python3 <scripts>/carry <folder> <work as JSON>` in a session of its own, so
    that closing the caller's session doesn't stop it, with what it writes on stdout and stderr,
    such as a traceback, appended to the folder's `log`.
    """
    with open(os.path.join(folder, LOG), "a", encoding="utf-8") as log:
        subprocess.Popen(
            [sys.executable, CARRY, folder, json.dumps(work._asdict())],
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
            start_new_session=True,
        )


def work_of(text: str) -> Work:
    """The work that `start` gave the carry package as JSON."""
    return Work(**json.loads(text))


def carry(
    folder: str,
    work: Work,
    host: claude.Host,
    now: Callable[[], datetime.datetime],
    sleep: Callable[[float], None],
) -> None:
    """Carries the work until a run is done or the retries run out.

    Takes: the work's folder, which exists, the work, the host that runs `claude`, the clock that
    gives the local time, and the sleep that waits for a number of seconds.
    Changes: runs `claude` in the work's folder, first with the prompt, then, after each stop and
    its wait, with `continue` in the last session that a run named, or with the prompt again where
    no run named one. Appends to the folder's `log` a line as each run starts and ends, and the
    work's end, `work <id> done after <n> runs` or `work <id> failed after <n> runs`, with `<id>`
    the folder's name. Writes `state.json` after each run: `status`, as `running`, `done`, or
    `failed`, the work's `dir`, the last `session_id` that a run named, or null, and the `runs`.
    """
    session: str | None = None
    run = 0
    # Each run ends the work or waits for the next, so the loop ends only where a run ends it.
    while True:
        run += 1
        _log_run(folder, now(), run, "started")
        stdin = work.prompt if session is None else CONTINUE
        read = claude.read(host(claude.command(work.tools, session), work.dir, stdin))
        session = read.session or session
        status = _status(read.done, run > work.retries)
        _state(folder, {"status": status, "dir": work.dir, "session_id": session, "runs": run})
        if status != "running":
            _ended(folder, now(), run, read, status)
            return
        wait = WAITS[min(run, len(WAITS)) - 1]
        at = now() + datetime.timedelta(minutes=wait)
        retry = f"Retry {run} of {work.retries} at {at:%H:%M}."
        _log_run(folder, now(), run, f"{_stopped(read)} {retry}")
        sleep(wait * 60)


def _status(done: bool, last: bool) -> str:
    if done:
        return "done"
    return "failed" if last else "running"


def _stopped(read: claude.Read) -> str:
    return f"stopped: {read.why.rstrip('.')}."


def _ended(folder: str, at: datetime.datetime, run: int, read: claude.Read, status: str) -> None:
    what = "done" if read.done else f"{_stopped(read)} No retries left."
    _log_run(folder, at, run, what)
    runs = "1 run" if run == 1 else f"{run} runs"
    _log(folder, f"work {os.path.basename(folder)} {status} after {runs}")


def _log_run(folder: str, at: datetime.datetime, run: int, what: str) -> None:
    _log(folder, f"{at:%H:%M} run {run} {what}")


def _log(folder: str, line: str) -> None:
    with open(os.path.join(folder, LOG), "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _state(folder: str, state: dict[str, object]) -> None:
    with open(os.path.join(folder, "state.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")
