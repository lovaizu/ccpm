"""The unit cases of plugins/overnight/scripts/overnight.py, with stand-ins in place of `claude`, of
`sleep`, and of the clock, so that a night's batch of hours runs in a moment: each refusal of the
arguments, before anything starts; the start of the batch in a process of its own, and that
process running the batch to its end; and the batch itself, which runs each work by `claude -p` in
its worktree, up to the given number at once, resumes a work that exits non-zero in the same
session after a wait that starts at 5 minutes and doubles to 60, gives it up after 6 hours of
waiting in all, waits for --at before it starts, and notes each of these in its record.

## Report

`uv run sh dev/scripts/check.sh` runs these cases with the rest of ccpm's, and reports each case
that fails with its assertion, then each line and branch of overnight.py that no case ran. The
report serves the decision whether step 1's logic works: every case passes, and the cases run
every line and branch.

## Records

Each case keeps what it checks in its own `tmp_path`, which pytest makes empty for it:

- `batch/record`, or `state/overnight/<YYYYmmdd-HHMMSS>/record` where overnight starts the batch
  itself: the batch's record, one line for each thing it noted
- `batch/<session id>.log`: the output of each run of a work
- `Night.claude.calls` and `Night.clock.slept`: each run of `claude` with its worktree, and each
  wait

## Checks of a run

Each case below, named by what overnight does.

## Checks and judges

No point is left to a judge, as code decides each. The stand-in of `claude` gives overnight only
what `claude -p` gives it: an exit code, with output on stdout. The stand-in of the clock moves
only as the batch sleeps. Each case was seen failing on a copy of overnight.py broken in what the
case checks.

## Stages

- One case, `test_a_work_that_ends_runs_once_and_is_noted`: tmp_path of the case.
- Each case once: tmp_path of each case.
- Every line and branch: coverage's report of check.sh, at 100%.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import stat
import sys
import threading
import time
import uuid
from datetime import datetime
from typing import Any, ClassVar

import pytest

# The top of the repository, four folders above this file.
TOP = os.path.abspath(os.path.join(os.path.dirname(__file__), *[os.pardir] * 4))
SCRIPT = os.path.join(TOP, "plugins", "overnight", "scripts", "overnight.py")
_SPEC = importlib.util.spec_from_file_location("overnight", SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
overnight: Any = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(overnight)

USAGE = "usage: overnight [--at HH:MM] <parallel> <worktree>...\n"
GO_ON = "Go on from where you stopped."
START = datetime(2026, 11, 27, 22, 30, 15)
# The waits before each resume of a work that never ends: 5 minutes doubling to 60, then what's
# left of 6 hours.
WAITS = [300, 600, 1200, 2400, 3600, 3600, 3600, 3600, 2700]


class Clock:
    """The clock and sleep of the batch, which moves only as the batch sleeps, each wait kept."""

    def __init__(self, start: datetime) -> None:
        self.time = start
        self.slept: list[float] = []
        self._lock = threading.Lock()

    def now(self) -> datetime:
        return self.time

    def sleep(self, seconds: float) -> None:
        with self._lock:
            self.slept.append(seconds)
            self.time = datetime.fromtimestamp(self.time.timestamp() + seconds)


class Claude:
    """`claude` as overnight runs it: each run gives the next exit code of its worktree, 0 once
    they run out, writes a line on its stdout, and is kept with its worktree and arguments."""

    def __init__(self) -> None:
        self.codes: dict[str, list[int]] = {}
        self.calls: list[tuple[str, list[str]]] = []
        self._lock = threading.Lock()

    def call(self, command: list[str], **how: Any) -> int:
        with self._lock:
            self.calls.append((how["cwd"], command))
            left = self.codes.get(how["cwd"], [])
            code = left.pop(0) if left else 0
        how["stdout"].write(f"run {len(self.calls)}\n".encode())
        return code


class Night:
    """What a case runs overnight in: its folder, an environment whose PATH holds an executable
    `claude` and whose state lies in the folder, the clock, and the stand-in of `claude`."""

    def __init__(self, top: str, monkeypatch: pytest.MonkeyPatch) -> None:
        self.top = top
        self.path = os.path.join(top, "bin")
        os.makedirs(self.path)
        executable(os.path.join(self.path, "claude"), "import sys\nsys.exit(0)\n")
        self.environ = {
            "HOME": os.path.join(top, "home"),
            "XDG_STATE_HOME": os.path.join(top, "state"),
            "PATH": self.path,
        }
        self.clock = Clock(START)
        self.claude = Claude()
        self.monkeypatch = monkeypatch

    def worktrees(self, *names: str) -> list[str]:
        """A folder for each name, as a worktree of rn's."""
        folders = []
        for name in names:
            folder = os.path.join(self.top, name)
            os.makedirs(folder)
            folders.append(folder)
        return folders

    def main(self, argv: list[str]) -> int:
        return overnight.main(argv, self.environ, self.clock.sleep, self.clock.now)

    def batch(self, arguments: list[str]) -> list[str]:
        """Runs the batch as its own process runs it, with the stand-in of `claude`, and gives its
        record's lines."""
        self.monkeypatch.setattr(overnight.subprocess, "call", self.claude.call)
        folder = os.path.join(self.top, "batch")
        os.makedirs(folder, exist_ok=True)
        assert self.main(["--batch", folder, *arguments]) == 0
        with open(os.path.join(folder, "record"), encoding="utf-8") as record:
            return record.read().splitlines()

    def log(self, session: str) -> str:
        """The output of each run of the session's work."""
        with open(os.path.join(self.top, "batch", f"{session}.log"), encoding="utf-8") as log:
            return log.read()


@pytest.fixture
def night(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Night:
    return Night(str(tmp_path), monkeypatch)


def executable(file: str, code: str) -> None:
    """Writes `code` as a Python script that runs on its own."""
    with open(file, "w", encoding="utf-8") as script:
        script.write(f"#!{sys.executable}\n{code}")
    os.chmod(file, os.stat(file).st_mode | stat.S_IXUSR)


def what(lines: list[str]) -> list[str]:
    """Each line of a record without its time, which must be `YYYY-mm-dd HH:MM:SS`."""
    for line in lines:
        assert re.match(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d ", line), line
    return [line[20:] for line in lines]


def session_of(command: list[str]) -> str:
    """The session id that a run of `claude` starts or resumes."""
    for option in ("--session-id", "--resume"):
        if option in command:
            return command[command.index(option) + 1]
    raise AssertionError(f"no session in {command}")


# The arguments


@pytest.mark.parametrize(
    "argv",
    [[], ["2"], ["--at"], ["--at", "23:00"], ["--at", "23:00", "2"], ["--batch"]],
)
def test_arguments_that_lack_a_part_give_the_usage(
    argv: list[str], night: Night, capsys: pytest.CaptureFixture[str]
):
    """Given arguments without <parallel>, a worktree, or the time of --at
    When overnight runs
    Then it gives 2 and the usage on stderr, and starts nothing"""
    assert night.main(argv) == 2
    assert capsys.readouterr().err == USAGE
    assert not os.path.exists(night.environ["XDG_STATE_HOME"])


@pytest.mark.parametrize(
    ("argv", "wrong"),
    [
        (["0", "{w}"], "<parallel> must be a whole number from 1, not '0'"),
        (["two", "{w}"], "<parallel> must be a whole number from 1, not 'two'"),
        (["--at", "24:00", "2", "{w}"], "--at takes the time to start as HH:MM"),
        (["--at", "7pm", "2", "{w}"], "not '7pm'"),
        (["--at", "23:0", "2", "{w}"], "not '23:0'"),
        (["2", "{w}", "{w}/missing"], "missing isn't a folder; give each worktree as a folder"),
    ],
)
def test_arguments_that_cant_run_a_batch_are_refused(
    argv: list[str], wrong: str, night: Night, capsys: pytest.CaptureFixture[str]
):
    """Given <parallel> that isn't a whole number from 1, a time that isn't HH:MM of a 24-hour
    day, or a worktree that isn't a folder
    When overnight runs
    Then it gives 1 and says on stderr what's wrong, and starts nothing"""
    (folder,) = night.worktrees("w")
    assert night.main([part.replace("{w}", folder) for part in argv]) == 1
    err = capsys.readouterr().err
    assert err.startswith("overnight: ")
    assert wrong in err
    assert not os.path.exists(night.environ["XDG_STATE_HOME"])


def test_without_claude_on_the_path_its_refused(night: Night, capsys: pytest.CaptureFixture[str]):
    """Given a PATH that has no `claude`
    When overnight runs
    Then it gives 1 and says to install Claude Code or put its folder on the PATH"""
    (folder,) = night.worktrees("w")
    night.environ["PATH"] = os.path.join(night.top, "empty")
    assert night.main(["2", folder]) == 1
    assert "claude isn't on the PATH; install Claude Code" in capsys.readouterr().err


# The start


class Started:
    """subprocess.Popen as overnight starts the batch, kept with what it's given."""

    pid = 4242
    command: ClassVar[list[str]] = []
    how: ClassVar[dict[str, Any]] = {}

    def __init__(self, command: list[str], **how: Any) -> None:
        Started.command = command
        Started.how = how


@pytest.mark.parametrize("xdg", [True, False])
def test_it_starts_the_batch_in_a_process_of_its_own(
    xdg: bool, night: Night, capsys: pytest.CaptureFixture[str]
):
    """Given --at, <parallel>, and a worktree given from the current folder, with XDG_STATE_HOME
    set, or unset so that the state lies under HOME
    When overnight runs
    Then it starts itself with --batch and the batch's folder before those arguments, the
    worktree made absolute, in a session of its own with no stdin, its output in batch.log, and
    prints the process and its record, giving 0"""
    (folder,) = night.worktrees("w")
    if not xdg:
        night.environ["XDG_STATE_HOME"] = ""
    night.monkeypatch.chdir(night.top)
    night.monkeypatch.setattr(overnight.subprocess, "Popen", Started)
    assert night.main(["--at", "23:00", "2", "w"]) == 0
    state = night.environ["XDG_STATE_HOME"] or os.path.join(night.top, "home", ".local", "state")
    place = os.path.join(state, "overnight", "20261127-223015")
    assert Started.command == [
        sys.executable,
        SCRIPT,
        "--batch",
        place,
        "--at",
        "23:00",
        "2",
        folder,
    ]
    assert Started.how["stdin"] == overnight.subprocess.DEVNULL
    assert Started.how["start_new_session"] is True
    assert Started.how["stdout"].name == os.path.join(place, "batch.log")
    assert Started.how["env"] == night.environ
    assert capsys.readouterr().out == (
        "overnight: started the batch as process 4242, writing its record to"
        f" {os.path.join(place, 'record')}\n"
    )
    assert night.clock.slept == []


def test_where_caffeinate_is_on_the_path_the_batch_runs_under_it(night: Night):
    """Given a PATH that has `caffeinate`, as a Mac's has, and no --at
    When overnight runs
    Then it starts the batch under `caffeinate -i`, so that the Mac doesn't sleep, with no --at"""
    (folder,) = night.worktrees("w")
    executable(os.path.join(night.path, "caffeinate"), "")
    night.monkeypatch.setattr(overnight.subprocess, "Popen", Started)
    assert night.main(["1", folder]) == 0
    place = os.path.join(night.environ["XDG_STATE_HOME"], "overnight", "20261127-223015")
    assert Started.command == [
        "caffeinate",
        "-i",
        sys.executable,
        SCRIPT,
        "--batch",
        place,
        "1",
        folder,
    ]


def test_the_started_process_runs_the_batch_to_its_end(
    night: Night, capsys: pytest.CaptureFixture[str]
):
    """Given a `claude` that keeps each run's folder and arguments and ends at once
    When overnight runs for real, with the environment of the tests beside its own
    Then the process it started runs the work in its worktree with `claude -p` and /rn:up, notes
    its end and the batch's in the record, and ends with nothing on its own output"""
    (folder,) = night.worktrees("w")
    calls = os.path.join(night.top, "calls")
    executable(
        os.path.join(night.path, "claude"),
        "import json, os, sys\n"
        f"with open({calls!r}, 'a') as calls:\n"
        "    calls.write(json.dumps([os.getcwd(), sys.argv[1:]]) + '\\n')\n",
    )
    assert overnight.main(["1", folder], {**os.environ, **night.environ}) == 0
    started = r"overnight: started the batch as process (\d+), writing its record to (\S+)\n"
    printed = re.fullmatch(started, capsys.readouterr().out)
    assert printed is not None
    pid, record = int(printed.group(1)), printed.group(2)
    deadline = time.monotonic() + 60
    while os.waitpid(pid, os.WNOHANG) == (0, 0):
        assert time.monotonic() < deadline, "the batch didn't end within 60 seconds"
        time.sleep(0.05)
    with open(calls, encoding="utf-8") as ran:
        ((cwd, arguments),) = [json.loads(line) for line in ran]
    session = session_of(arguments)
    assert cwd == folder
    assert (arguments[0], arguments[-1]) == ("-p", "/rn:up")
    with open(record, encoding="utf-8") as lines:
        noted = what(lines.read().splitlines())
    assert noted[1:] == [f"{folder}: ended after 0 resumes in session {session}", "the batch ended"]
    with open(os.path.join(os.path.dirname(record), "batch.log"), encoding="utf-8") as log:
        assert log.read() == ""


# The batch


def test_a_work_that_ends_runs_once_and_is_noted(night: Night):
    """Given one worktree whose run of rn ends with 0
    When the batch runs
    Then it runs `claude -p` once in the worktree, in a new session on no model of its own, with
    rn's /rn:up and the prompt that leaves the user's points for the morning, appends its output
    to the session's log, waits for nothing, and notes the start, the end, and the batch's end,
    each at the time it happened"""
    (folder,) = night.worktrees("w")
    lines = night.batch(["1", folder])
    ((cwd, command),) = night.claude.calls
    session = session_of(command)
    assert uuid.UUID(session).version == 4
    assert cwd == folder
    assert command[:3] == ["claude", "-p", "--append-system-prompt"]
    assert "no one is at hand to answer" in command[3]
    assert "leave the point as the question for the morning" in command[3]
    assert command[4:] == ["--session-id", session, "/rn:up"]
    log = os.path.join(night.top, "batch", f"{session}.log")
    assert lines == [
        f"2026-11-27 22:30:15 {folder}: started in session {session}, writing its output to {log}",
        f"2026-11-27 22:30:15 {folder}: ended after 0 resumes in session {session}",
        "2026-11-27 22:30:15 the batch ended",
    ]
    assert night.log(session) == "run 1\n"
    assert night.clock.slept == []


def test_a_work_that_fails_resumes_its_session_until_it_ends(night: Night):
    """Given a worktree whose run exits 1, as at the usage limit, then 1 on its first resume, and
    ends on its second
    When the batch runs
    Then it waits 5 minutes, resumes the same session to go on on no model of its own, waits 10,
    resumes again, and notes each failure with its exit code, each resume with its count, and
    the end after 2 resumes, with every run's output in the one log"""
    (folder,) = night.worktrees("w")
    night.claude.codes[folder] = [1, 1, 0]
    lines = night.batch(["1", folder])
    session = session_of(night.claude.calls[0][1])
    assert [command[4:] for _, command in night.claude.calls] == [
        ["--session-id", session, "/rn:up"],
        ["--resume", session, GO_ON],
        ["--resume", session, GO_ON],
    ]
    assert night.clock.slept == [300, 600]
    assert lines[1:] == [
        f"2026-11-27 22:30:15 {folder}: failed with exit 1 in session {session}",
        f"2026-11-27 22:35:15 {folder}: resume 1 in session {session}",
        f"2026-11-27 22:35:15 {folder}: failed with exit 1 in session {session}",
        f"2026-11-27 22:45:15 {folder}: resume 2 in session {session}",
        f"2026-11-27 22:45:15 {folder}: ended after 2 resumes in session {session}",
        "2026-11-27 22:45:15 the batch ended",
    ]
    assert night.log(session) == "run 1\nrun 2\nrun 3\n"


def test_a_work_that_never_ends_is_given_up_after_6_hours_of_waiting(night: Night):
    """Given a worktree whose every run exits 1
    When the batch runs
    Then the waits double from 5 minutes to 60, the last cut to what's left of 6 hours, and
    after the resume that follows it fails, the work is given up with the 360 minutes waited and
    the 9 resumes noted, and the batch ends"""
    (folder,) = night.worktrees("w")
    night.claude.codes[folder] = [1] * 20
    lines = night.batch(["1", folder])
    session = session_of(night.claude.calls[0][1])
    assert night.clock.slept == WAITS
    assert sum(WAITS) == 6 * 60 * 60
    assert len(night.claude.calls) == 10
    assert what(lines)[-3:] == [
        f"{folder}: failed with exit 1 in session {session}",
        f"{folder}: given up after 360 minutes of waiting in all, 9 resumes, in session {session}",
        "the batch ended",
    ]


def test_each_work_has_its_own_session_and_waits(night: Night):
    """Given two worktrees, one whose first run exits 2 and one that ends at once, run one at a
    time
    When the batch runs
    Then each runs in its own worktree and session, only the one that failed waits and resumes,
    and each end is noted"""
    first, second = night.worktrees("a", "b")
    night.claude.codes[first] = [2]
    noted = what(night.batch(["1", first, second]))
    sessions = {cwd: session_of(command) for cwd, command in night.claude.calls}
    assert len(set(sessions.values())) == 2
    assert [cwd for cwd, _ in night.claude.calls] == [first, first, second]
    assert night.clock.slept == [300]
    assert f"{first}: failed with exit 2 in session {sessions[first]}" in noted
    assert f"{first}: ended after 1 resumes in session {sessions[first]}" in noted
    assert f"{second}: ended after 0 resumes in session {sessions[second]}" in noted


def test_it_runs_up_to_the_given_number_of_works_at_once(night: Night):
    """Given three worktrees and a parallel count of 2
    When the batch runs
    Then the first two works run at the same time, no more than two ever run at once, and all
    three end"""
    folders = night.worktrees("a", "b", "c")
    claude = night.claude
    together = threading.Barrier(2, timeout=10)
    running = {"now": 0, "most": 0}
    lock = threading.Lock()

    def call(command: list[str], **how: Any) -> int:
        with lock:
            running["now"] += 1
            running["most"] = max(running.values())
            first = len(claude.calls) < 2
        if first:
            together.wait()
        try:
            return Claude.call(claude, command, **how)
        finally:
            with lock:
                running["now"] -= 1

    night.claude.call = call
    night.batch(["2", *folders])
    assert running["most"] == 2
    assert sorted(cwd for cwd, _ in claude.calls) == folders


def test_an_error_a_work_meets_stops_the_batch_with_its_trace(night: Night):
    """Given a worktree where `claude` can't be run, such as one removed after the start
    When the batch runs
    Then the error comes out of the batch, and the batch's end isn't noted"""
    (folder,) = night.worktrees("w")

    def call(command: list[str], **how: Any) -> int:
        raise FileNotFoundError(how["cwd"])

    night.claude.call = call
    with pytest.raises(FileNotFoundError):
        night.batch(["1", folder])
    with open(os.path.join(night.top, "batch", "record"), encoding="utf-8") as record:
        assert "the batch ended" not in record.read()


@pytest.mark.parametrize(
    ("start", "at", "wait"),
    [
        (START, "23:00", 29 * 60 + 45),
        (datetime(2026, 11, 27, 23, 30), "23:00", 23.5 * 60 * 60),
        (datetime(2026, 11, 27, 23, 30), "0:05", 35 * 60),
        (datetime(2026, 11, 27, 23, 0), "23:00", 0),
        (datetime(2026, 11, 27, 23, 0, 0, 500000), "23:00", 0),
    ],
)
def test_with_at_the_batch_waits_until_the_next_such_time(
    start: datetime, at: str, wait: float, night: Night
):
    """Given --at with a time later today, earlier today, after midnight, or now
    When the batch runs
    Then it notes that it waits until that time, and waits until its next coming, today or
    tomorrow, or not at all where it's that minute now, before the first work starts"""
    (folder,) = night.worktrees("w")
    night.clock = Clock(start)
    lines = night.batch(["--at", at, "1", folder])
    assert night.clock.slept == [wait]
    assert what(lines)[0] == f"the batch waits until {at} to start"
    started = datetime.fromtimestamp(start.timestamp() + wait)
    assert lines[1].startswith(started.strftime("%Y-%m-%d %H:%M:%S"))
    assert len(night.claude.calls) == 1
