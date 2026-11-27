"""Decides how a night's batch runs rn's works in its own process, how it resumes each work that
exits non-zero, such as at the usage limit, and what it records of each for the morning.

`bin/overnight [--at HH:MM] <parallel> <worktree>...` runs `main`. Each work is a run of rn in
its worktree, by `claude -p`, and up to <parallel> of them run at once. A work that exits
non-zero resumes in the same session, on the model it started on, after a wait that starts at 5
minutes and doubles to 60, and is given up after 6 hours of waiting in all. With --at, the batch
waits until the next HH:MM, today or tomorrow, before it starts."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid
from collections.abc import Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Callable, NamedTuple

_USAGE = "usage: overnight [--at HH:MM] <parallel> <worktree>...\n"

# Where a run comes to a point that is the user's to decide, no one is at hand to answer it until
# the morning.
_NIGHT = (
    "This run is a night's batch, and no one is at hand to answer. Where the run comes to a point"
    " that is the user's to decide, stop there and leave the point as the question for the"
    " morning."
)
_FIRST_WAIT = 5 * 60
_LONGEST_WAIT = 60 * 60
_ALL_WAITING = 6 * 60 * 60

_AT = re.compile(r"([01]?[0-9]|2[0-3]):([0-5][0-9])")


class _Wrong(Exception):
    """An input from outside that overnight refuses, said so that whoever ran it can mend it."""


class _Plan(NamedTuple):
    at: str | None
    parallel: int
    worktrees: list[str]


def main(
    argv: Sequence[str],
    environ: Mapping[str, str],
    sleep: Callable[[float], None] = time.sleep,
    now: Callable[[], datetime] = datetime.now,
) -> int:
    """Runs overnight with `argv`, the arguments after the command's name, and gives its exit code.

    With `[--at HH:MM] <parallel> <worktree>...`, it makes the batch's folder
    `$XDG_STATE_HOME/overnight/<YYYYmmdd-HHMMSS>`, or `~/.local/state/overnight/...` where
    XDG_STATE_HOME is unset, starts the batch there in a process of its own, in a session of its
    own so that closing the terminal leaves it running and under `caffeinate -i` where the PATH
    has it, prints `overnight: started the batch as process <pid>, writing its record to
    <folder>/record`, and gives 0.

    With `--batch <folder>` before those arguments, as that process is started, it runs the batch
    itself and gives 0 once every work has ended or been given up: it notes in `<folder>/record`,
    one line each, `<YYYY-mm-dd HH:MM:SS> <what>`, when the batch waits for --at, each start,
    failure with its exit code, resume with its count, end, or giving up of each work with its
    worktree and session id, and the batch's end. Each work's runs append their output to
    `<folder>/<session id>.log`. `sleep` waits the seconds given, and `now` gives the local time.

    Refuses, giving 2 and the usage on stderr, where the arguments lack <parallel> or a worktree,
    or --at lacks its time. Refuses, giving 1 with `overnight: <what's wrong>` on stderr and having
    started nothing, where the time isn't HH:MM of a 24-hour day, <parallel> isn't a whole number
    from 1, a worktree isn't a folder, or `claude` isn't on the PATH of `environ`."""
    batch = None
    if argv[:1] == ["--batch"] and len(argv) > 1:
        batch, argv = argv[1], argv[2:]
    try:
        plan = _read(argv)
        if plan is not None:
            _check(plan, environ)
    except _Wrong as wrong:
        sys.stderr.write(f"overnight: {wrong}\n")
        return 1
    if plan is None:
        sys.stderr.write(_USAGE)
        return 2
    if batch is not None:
        _Batch(batch, environ, sleep, now).run(plan)
        return 0
    folder = os.path.join(
        environ.get("XDG_STATE_HOME") or os.path.join(environ["HOME"], ".local", "state"),
        "overnight",
        now().strftime("%Y%m%d-%H%M%S"),
    )
    os.makedirs(folder, exist_ok=True)
    print(
        f"overnight: started the batch as process {_start(plan, folder, environ)}, writing its"
        f" record to {os.path.join(folder, 'record')}"
    )
    return 0


def _read(argv: Sequence[str]) -> _Plan | None:
    """The plan that the arguments give, or None where they lack a part of the usage. Raises
    _Wrong where <parallel> isn't a whole number from 1."""
    at = None
    if argv[:1] == ["--at"]:
        if len(argv) < 2:
            return None
        at, argv = argv[1], argv[2:]
    if len(argv) < 2:
        return None
    # isdigit() alone takes such digits as ², which int() can't read.
    if not (argv[0].isascii() and argv[0].isdigit()) or int(argv[0]) < 1:
        raise _Wrong(f"<parallel> must be a whole number from 1, not {argv[0]!r}")
    return _Plan(at, int(argv[0]), [os.path.abspath(worktree) for worktree in argv[1:]])


def _check(plan: _Plan, environ: Mapping[str, str]) -> None:
    """Raises _Wrong where the time, a worktree, or the PATH can't run the batch."""
    if plan.at is not None and not _AT.fullmatch(plan.at):
        raise _Wrong(
            f"--at takes the time to start as HH:MM of a 24-hour day, such as 23:00, not"
            f" {plan.at!r}"
        )
    for worktree in plan.worktrees:
        if not os.path.isdir(worktree):
            raise _Wrong(f"{worktree} isn't a folder; give each worktree as a folder that exists")
    if shutil.which("claude", path=environ.get("PATH")) is None:
        raise _Wrong("claude isn't on the PATH; install Claude Code, or put its folder on the PATH")


def _start(plan: _Plan, folder: str, environ: Mapping[str, str]) -> int:
    """Starts the batch of the plan in a process of its own, and gives its process id."""
    command = [sys.executable, os.path.abspath(__file__), "--batch", folder]
    if plan.at is not None:
        command += ["--at", plan.at]
    command += [str(plan.parallel), *plan.worktrees]
    # A Mac that sleeps would pause the batch with it.
    if shutil.which("caffeinate", path=environ.get("PATH")) is not None:
        command = ["caffeinate", "-i", *command]
    with open(os.path.join(folder, "batch.log"), "ab") as log:
        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            env=dict(environ),
            start_new_session=True,
        )
    return process.pid


class _Batch:
    """One night's batch, writing its record in its folder."""

    def __init__(
        self,
        folder: str,
        environ: Mapping[str, str],
        sleep: Callable[[float], None],
        now: Callable[[], datetime],
    ) -> None:
        self._folder = folder
        self._environ = dict(environ)
        self._sleep = sleep
        self._now = now
        self._lock = threading.Lock()

    def run(self, plan: _Plan) -> None:
        if plan.at is not None:
            self._note(f"the batch waits until {plan.at} to start")
            self._sleep(_until(plan.at, self._now()))
        with ThreadPoolExecutor(max_workers=plan.parallel) as pool:
            # list() raises here an error that a work met, with its trace.
            list(pool.map(self._work, plan.worktrees))
        self._note("the batch ended")

    def _work(self, worktree: str) -> None:
        """Runs one work to its end, or until it's given up."""
        session = str(uuid.uuid4())
        output = os.path.join(self._folder, f"{session}.log")
        self._note(f"{worktree}: started in session {session}, writing its output to {output}")
        # No --model, so a resume runs on the model the work started on.
        code = self._claude(worktree, output, ["--session-id", session, "/rn:up"])
        waited, wait, resumes = 0, _FIRST_WAIT, 0
        while code != 0:
            self._note(f"{worktree}: failed with exit {code} in session {session}")
            if waited >= _ALL_WAITING:
                self._note(
                    f"{worktree}: given up after {waited // 60} minutes of waiting in all,"
                    f" {resumes} resumes, in session {session}"
                )
                return
            wait = min(wait, _ALL_WAITING - waited)
            self._sleep(wait)
            waited += wait
            wait = min(wait * 2, _LONGEST_WAIT)
            resumes += 1
            self._note(f"{worktree}: resume {resumes} in session {session}")
            code = self._claude(
                worktree, output, ["--resume", session, "Go on from where you stopped."]
            )
        self._note(f"{worktree}: ended after {resumes} resumes in session {session}")

    def _claude(self, worktree: str, output: str, arguments: list[str]) -> int:
        """Runs `claude -p` in the worktree, appending its output to the file, and gives its exit
        code."""
        with open(output, "ab") as log:
            return subprocess.call(
                ["claude", "-p", "--append-system-prompt", _NIGHT, *arguments],
                cwd=worktree,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                env=self._environ,
            )

    def _note(self, what: str) -> None:
        line = f"{self._now().strftime('%Y-%m-%d %H:%M:%S')} {what}\n"
        with (
            self._lock,
            open(os.path.join(self._folder, "record"), "a", encoding="utf-8") as record,
        ):
            record.write(line)


def _until(at: str, now: datetime) -> float:
    """The seconds from now until the next `at`, today or tomorrow, or 0 where it's `at` now."""
    hour, minute = (int(part) for part in at.split(":"))
    start = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if start < now.replace(microsecond=0):
        start += timedelta(days=1)
    return max((start - now).total_seconds(), 0.0)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:], os.environ))
