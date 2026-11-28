"""When one work's runs are asked of Claude Code: the retries in the same conversation, the waits
before each, and what each run adds to the work's state and log."""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from overnight import claude, record

# What a retry asks Claude, in the conversation that the stop left, as a user at the keyboard would
# type once the limit lifts.
GO_ON = "Go on with the work from where it stopped."
# The waits before the first retries, then before each after them: 5 and 10 minutes catch a short
# error soon, and 60 minutes each make the 7 retries of the default wait 5 hours and 15 minutes in
# all, past the 5-hour limit after any stop, while the work goes on within an hour of its lifting.
_FIRST_WAITS = (timedelta(minutes=5), timedelta(minutes=10))
_LATER_WAIT = timedelta(minutes=60)


@dataclass(frozen=True)
class Work:
    """A work: the `dir` it runs in, the `allowed_tools` that Claude may use, as
    `claude --allowed-tools` takes them, its `prompt`, and how many `retries` it may have."""

    dir: str
    allowed_tools: str
    prompt: str
    retries: int


@dataclass(frozen=True)
class Clock:
    """What gives the time, `now`, and what waits, `sleep`, which takes seconds."""

    now: Callable[[], datetime] = datetime.now
    sleep: Callable[[float], None] = time.sleep


def carry(folder: str, work: Work, clock: Clock) -> record.State:
    """Runs `work` through Claude Code until a run is done or its retries run out, writing its state
    in `folder`, the work's folder that record.start made, after each run, and a line in its log as
    each run starts and ends. A run that Claude Code can't start, such as when the work's folder is
    gone, is a stop like any other, retried until the retries run out. Gives the work's last state:
    done or failed."""
    session_id: str | None = None
    runs = 0
    while True:
        runs += 1
        record.log(folder, f"{_hhmm(clock.now())} run {runs} started")
        prompt = work.prompt if session_id is None else GO_ON
        reply = claude.ask(work.dir, work.allowed_tools, prompt, session_id)
        session_id = reply.session_id or session_id
        if reply.done:
            state = record.State("done", work.dir, session_id, runs)
            return _end(folder, state, f"{_hhmm(clock.now())} run {runs} done")
        stop = f"{_hhmm(clock.now())} run {runs} stopped: {reply.reason}."
        if runs > work.retries:
            state = record.State("failed", work.dir, session_id, runs)
            return _end(folder, state, f"{stop} No retries left.")
        record.write(folder, record.State("running", work.dir, session_id, runs))
        wait = _wait_before(runs)
        at = _hhmm(clock.now() + wait)
        record.log(folder, f"{stop} Retry {runs} of {work.retries} at {at}.")
        clock.sleep(wait.total_seconds())


def main(argv: list[str]) -> None:
    """Carries the work that `argv` names, as the command passes it: the work's folder, the folder
    it runs in, its allowed tools, its retries as a whole number, and its prompt."""
    folder, directory, allowed_tools, retries, prompt = argv
    carry(folder, Work(directory, allowed_tools, prompt, int(retries)), Clock())


def _wait_before(retry: int) -> timedelta:
    """The wait before retry `retry`, counted from 1."""
    if retry <= len(_FIRST_WAITS):
        return _FIRST_WAITS[retry - 1]
    return _LATER_WAIT


def _end(folder: str, state: record.State, last: str) -> record.State:
    """Writes the work's last `state`, and logs `last`, the line of its last run, then the work's
    end."""
    record.write(folder, state)
    runs = f"{state.runs} run" if state.runs == 1 else f"{state.runs} runs"
    record.log(folder, last)
    record.log(folder, f"work {os.path.basename(folder)} {state.status} after {runs}")
    return state


def _hhmm(moment: datetime) -> str:
    return moment.strftime("%H:%M")
