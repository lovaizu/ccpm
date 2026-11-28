"""Decides the course of one work: its runs of `claude`, the waits between them, when the work is
done or failed, and what its folder records of it, in `work.json`, `state.json`, and `log`."""

from __future__ import annotations

import datetime
import json
import os
from collections.abc import Mapping
from typing import Any, Callable, NamedTuple

from overnight import claude

# The minutes to wait before each retry, the last for each retry after it. They grow so that a
# limit that holds gets few requests, and end at an hour so that the work goes on within an hour
# after the 5-hour limit lifts: 7 retries wait 275 minutes in all, which spans it.
WAITS = (5, 10, 20, 60)
# The retries of a work whose `--retries` the user doesn't give.
RETRIES = 7
# What a retry asks Claude, in the session where the run stopped, as the user would type it.
CONTINUE = "continue"
# The files of a work's folder: what the user asked, where the work stands, and its course.
WORK = "work.json"
STATE = "state.json"
LOG = "log"


class Work(NamedTuple):
    """One work: the folder Claude works in, the tools it may use, as `--allowed-tools` takes
    them, how many times a stopped run is retried, and the prompt."""

    dir: str
    tools: str
    retries: int
    prompt: str


def put(folder: str, work: Work) -> None:
    """Puts the work in its folder, which exists, to wait for its carry.

    Changes: writes `work.json`, then `state.json` with `status` `waiting`, the work's `dir`,
    `session_id` null, and `runs` 0, so that `status` gives a status only once both are written.
    """
    _write(os.path.join(folder, WORK), work._asdict())
    _state(folder, "waiting", work, None, 0)


def status(folder: str) -> str | None:
    """The work's status in the folder: `waiting`, `running`, `done`, or `failed`, or None where no
    work is put in it, such as a file or a folder that `put` hasn't finished."""
    path = os.path.join(folder, STATE)
    return _read(path)["status"] if os.path.isfile(path) else None


def carry(
    folder: str,
    host: claude.Host,
    now: Callable[[], datetime.datetime],
    sleep: Callable[[float], None],
) -> None:
    """Carries the work in the folder, from where its state stands, until a run is done or the
    retries run out.

    Takes: the folder of a work that `put` put there, which waits or runs, the host that runs
    `claude`, the clock that gives the local time, and the sleep that waits for a number of
    seconds.
    Changes: runs `claude` in the work's `dir`, first with the prompt, then, after each stop and
    its wait, with `continue` in the last session that a run named, or with the prompt again where
    no run named one. A work that was running, as a carry stopped, goes on at once with the run
    after its last that ended. Appends to the folder's `log` a line as each run starts and ends,
    and the work's end, `work <id> done after <n> runs` or `work <id> failed after <n> runs`, with
    `<id>` the folder's name. Writes `state.json` as the carry starts and after each run:
    `status`, as `running`, `done`, or `failed`, the work's `dir`, the last `session_id` that a run
    named, or null, and the `runs` that ended.
    """
    work = Work(**_read(os.path.join(folder, WORK)))
    state = _read(os.path.join(folder, STATE))
    session: str | None = state["session_id"]
    run: int = state["runs"]
    _state(folder, "running", work, session, run)
    # Each run ends the work or waits for the next, so the loop ends only where a run ends it.
    while True:
        run += 1
        _log_run(folder, now(), run, "started")
        stdin = work.prompt if session is None else CONTINUE
        read = claude.read(host(claude.command(work.tools, session), work.dir, stdin))
        session = read.session or session
        status = _status(read.done, run > work.retries)
        _state(folder, status, work, session, run)
        if status != "running":
            _ended(folder, now(), run, read, status)
            return
        wait = WAITS[min(run, len(WAITS)) - 1]
        at = now() + datetime.timedelta(minutes=wait)
        retry = f"Retry {run} of {work.retries} at {at:%H:%M}."
        _log_run(folder, now(), run, f"{_stopped(read)} {retry}")
        sleep(wait * 60)


def fail(folder: str, at: datetime.datetime, error: Exception) -> None:
    """Records the work in the folder as failed, where an error that its carry raised stopped it,
    such as a `dir` that is gone, as no retry would go on from there.

    Takes: the folder of a work that `put` put there, the local time, and the error.
    Changes: appends to the folder's `log` `<hh:mm> stopped: <error>. No retries.` and
    `work <id> failed after <n> runs`, with `<n>` the runs that ended, and writes `state.json` with
    `status` `failed`, the rest as it stood.
    """
    state = _read(os.path.join(folder, STATE))
    _log(folder, f"{at:%H:%M} stopped: {type(error).__name__}: {error}. No retries.")
    _log_end(folder, "failed", state["runs"])
    _write(os.path.join(folder, STATE), {**state, "status": "failed"})


def _status(done: bool, last: bool) -> str:
    if done:
        return "done"
    return "failed" if last else "running"


def _stopped(read: claude.Read) -> str:
    return f"stopped: {read.why.rstrip('.')}."


def _ended(folder: str, at: datetime.datetime, run: int, read: claude.Read, status: str) -> None:
    what = "done" if read.done else f"{_stopped(read)} No retries left."
    _log_run(folder, at, run, what)
    _log_end(folder, status, run)


def _log_end(folder: str, status: str, runs: int) -> None:
    ran = "1 run" if runs == 1 else f"{runs} runs"
    _log(folder, f"work {os.path.basename(folder)} {status} after {ran}")


def _log_run(folder: str, at: datetime.datetime, run: int, what: str) -> None:
    _log(folder, f"{at:%H:%M} run {run} {what}")


def _log(folder: str, line: str) -> None:
    with open(os.path.join(folder, LOG), "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _state(folder: str, status: str, work: Work, session: str | None, runs: int) -> None:
    state = {"status": status, "dir": work.dir, "session_id": session, "runs": runs}
    _write(os.path.join(folder, STATE), state)


def _read(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write(path: str, content: Mapping[str, object]) -> None:
    # Written whole beside the file, then put in its place, so that a stop of the computer as it
    # writes leaves the file as it was, which a runner started again reads.
    beside = path + ".new"
    with open(beside, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2)
        f.write("\n")
    os.replace(beside, path)
