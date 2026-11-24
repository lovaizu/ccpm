"""What overnight's integration cases share: a bench that holds a copy of overnight, the person's
repository, the stand-in of Claude Code first on the PATH, and a clock of the bench's own; and the
moves of a night as overnight's architecture draws them under Sequences, each a handoff between its
scripts.

Each move runs overnight's scripts as its skills run them, from the repository's root, each in a
process of its own, as the AI's Bash tool runs them: handover.py as ask runs it, which starts the
runner apart from the session, and pieces.py as status runs it. In place of each prompt's work,
the case hands on the words that ask and status hand on. The bench's copy of overnight takes the
clock of the bench in place of its own, as `runner/clock.py` given again: its time is what the case
or a run of the stand-in sets, and a wait until a time moves it there at once, so that no case
waits a night, as overnight's Test strategy says under Integration testing."""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, NamedTuple

import overnight_files
from claude_code import claude_double
from overnight_files import PLUGIN, PROMPT, REPOSITORY, TOOLS_LINE

# The heading of the table that status shows, by which each row's fields are read.
COLUMNS = ("Piece", "State", "Branch", "Waited", "Last words")
# The longest that a script may take, so that one that never returns fails its case.
SCRIPT_LONGEST = 30.0


class Ran(NamedTuple):
    """What a script gave: its exit code, its stdout, and its stderr."""

    code: int
    out: str
    err: str


@dataclass(frozen=True)
class Bench:
    """A copy of overnight, the person's repository, the folder of the stand-in's state, the
    bench's clock and the files of its waits, the environment of each script, and what each
    hand-over gave."""

    plugin: str
    repo: str
    state: str
    clock: str
    env: dict[str, str]
    handed: list[Ran] = field(default_factory=list)

    def at(self, path: str) -> str:
        """The path in the person's repository."""
        return os.path.join(self.repo, path)

    def piece_folder(self, number: int) -> str:
        """Where the piece of the number works: `../<repository>-overnight-<n>/`."""
        return os.path.join(os.path.dirname(self.repo), f"{REPOSITORY}-overnight-{number}")

    def script(self, name: str, *args: str, stdin: str = "", cwd: str | None = None) -> Ran:
        """Runs one of overnight's scripts from the repository's root, or the folder given, as a
        skill runs it."""
        done = subprocess.run(
            [sys.executable, os.path.join(self.plugin, "scripts", f"{name}.py"), *args],
            input=stdin,
            capture_output=True,
            text=True,
            cwd=cwd or self.repo,
            env=self.env,
            timeout=SCRIPT_LONGEST,
            check=False,
        )
        return Ran(done.returncode, done.stdout, done.stderr)

    def hand(self, prompt: str = PROMPT, tools: str = TOOLS_LINE) -> Ran:
        """Hands a piece over as ask does: handover.py with the tools, the prompt on its stdin."""
        given = self.script("handover", tools, stdin=prompt)
        self.handed.append(given)
        return given

    def until(self, check: Callable[[], bool], what: str, timeout: float = 30.0) -> None:
        """Waits until the check gives true, or fails the case naming what it waited for, at once
        where a hand-over gave no piece to wait on."""

        def checked() -> bool:
            for each in self.handed:
                assert each.code == 0, f"a hand-over gave {each.code}: {each.err}"
            return check()

        overnight_files.until(checked, timeout, what)

    def status(self) -> Ran:
        """Shows where each piece stands as status does: pieces.py report."""
        return self.script("pieces", "report")

    def rows(self) -> list[dict[str, str]]:
        """Each row of the table that status shows, by its columns' names."""
        shown = self.status()
        assert shown.code == 0, shown.err
        return rows_of(shown.out)

    def plays(self, given: dict[str, list[dict[str, Any]]]) -> None:
        """Gives the stand-in of Claude Code its plays, by each piece's number."""
        claude_double.plays(self.state, given, self.clock)

    def calls(self, number: int | None = None) -> list[dict[str, Any]]:
        """Each run of the stand-in, or each in the folder of the piece of the number."""
        made = claude_double.calls(self.state)
        if number is None:
            return made
        folder = os.path.realpath(self.piece_folder(number))
        return [each for each in made if each["cwd"] == folder]

    def release(self, hold: str) -> None:
        """Releases the runs of the stand-in held by the name."""
        claude_double.release(self.state, hold)

    def runners(self) -> set[int]:
        """The ID of each runner's process, as the parent of each run of the stand-in."""
        return {each["ppid"] for each in self.calls()}

    def settle(self, pieces: int) -> list[dict[str, str]]:
        """Waits until the runner of each of the pieces made a run and ended, and gives the rows
        that status shows then."""
        self.until(
            lambda: (
                len(self.runners()) >= pieces
                and not any(map(overnight_files.alive, self.runners()))
            ),
            what=f"the runners of {pieces} pieces to end",
        )
        return self.rows()

    def set_clock(self, when: str) -> None:
        """Sets the bench's clock to the time, in the local zone."""
        kept = f"{self.clock}.case"
        with open(kept, "w", encoding="utf-8") as f:
            json.dump({"now": datetime.fromisoformat(when).astimezone().isoformat()}, f)
        os.replace(kept, self.clock)

    def hold_waits(self) -> None:
        """Holds each wait until a time, so that the case sees a piece while it waits."""
        with open(f"{self.clock}.hold", "w", encoding="utf-8"):
            pass

    def release_waits(self) -> None:
        """Lets each wait held go on."""
        if os.path.exists(f"{self.clock}.hold"):
            os.remove(f"{self.clock}.hold")

    def waits(self) -> list[dict[str, str]]:
        """Each wait until a time that a runner made on the bench's clock: from when, until when."""
        path = f"{self.clock}.waits"
        if not os.path.exists(path):
            return []
        with open(path, encoding="utf-8") as f:
            return [json.loads(each) for each in f if each.strip()]

    def end(self) -> None:
        """Releases each hold, and waits until each runner ended, as the case ends."""
        with open(os.path.join(self.state, claude_double.RELEASE_ALL), "w", encoding="utf-8"):
            pass
        self.release_waits()
        try:
            overnight_files.until(
                lambda: not any(map(overnight_files.alive, self.runners())),
                what="each runner to end",
            )
        except AssertionError:
            for pid in self.runners():
                overnight_files.kill(pid)


def rows_of(table: str) -> list[dict[str, str]]:
    """Each row of a table that status shows, read by where its heading puts each column."""
    lines = table.splitlines()
    starts = [lines[0].index(name) for name in COLUMNS]
    found = []
    for each in lines[1:]:
        if not each.strip():
            break
        ends = [*starts[1:], None]
        found.append({n: each[s:e].strip() for n, s, e in zip(COLUMNS, starts, ends)})
    return found


# The bench's clock, in place of overnight's: `<clock>` is the file of its time, `<clock>.hold`
# holds each wait while it's there, and `<clock>.waits` keeps each wait.
CLOCK = """
CLOCK = {clock!r}


def now():
    import json
    from datetime import datetime

    with open(CLOCK, encoding="utf-8") as f:
        return datetime.fromisoformat(json.load(f)["now"])


def wait_until(when):
    import json
    import os
    import time

    while os.path.exists(CLOCK + ".hold"):
        time.sleep(0.05)
    with open(CLOCK + ".waits", "a", encoding="utf-8") as f:
        f.write(json.dumps({{"from": now().isoformat(), "until": when.isoformat()}}) + "\\n")
    if when > now():
        kept = CLOCK + "." + str(os.getpid())
        with open(kept, "w", encoding="utf-8") as f:
            json.dump({{"now": when.isoformat()}}, f)
        os.replace(kept, CLOCK)
"""


def given_again(b: Bench, module: str, code: str) -> None:
    """Gives an interface of the module of the bench's copy of overnight again, at the end of its
    code, so that the one given again is the one each caller meets."""
    path = os.path.join(b.plugin, module)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    with open(path, "w", encoding="utf-8") as f:
        f.write(text + "\n\n" + code + "\n")


def bench(tmp: str) -> Bench:
    """A bench in the folder: a copy of overnight, the walkthrough's repository `myapp` with its
    first commit, the stand-in of Claude Code first on the PATH, and the bench's clock at 23:00 of
    the walkthrough's night."""
    plugin = os.path.join(tmp, "overnight")
    shutil.copytree(PLUGIN, plugin, ignore=shutil.ignore_patterns("__pycache__"))
    repo = overnight_files.repository(os.path.join(tmp, "work"))
    state = os.path.join(tmp, "claude")
    bin_folder = claude_double.program(os.path.join(tmp, "bin"), state)
    env = overnight_files.environment(tmp, [bin_folder])
    b = Bench(plugin, repo, state, os.path.join(tmp, "clock.json"), env)
    given_again(b, "domain/runner/clock.py", CLOCK.format(clock=b.clock))
    b.set_clock("2026-11-24T23:00:00")
    b.plays({})
    return b


def session(b: Bench, prompt: str = PROMPT, tools: str = TOOLS_LINE) -> tuple[Ran, int]:
    """Hands a piece over from a session of its own, as ask does in a terminal that the person may
    close, and gives what handover.py gave and the session's process group."""
    apart: dict[str, Any] = {"start_new_session": True}
    if os.name == "nt":
        apart = {"creationflags": getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)}
    started = subprocess.Popen(
        [sys.executable, os.path.join(b.plugin, "scripts", "handover.py"), tools],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=b.repo,
        env=b.env,
        **apart,
    )
    out, err = started.communicate(prompt, timeout=SCRIPT_LONGEST)
    given = Ran(started.returncode, out, err)
    b.handed.append(given)
    return given, started.pid


def close_session(group: int) -> None:
    """Closes the session of the process group, as closing its terminal does: each process left
    in the group gets the hang-up."""
    try:
        if os.name == "nt":
            os.kill(group, getattr(signal, "CTRL_BREAK_EVENT", signal.SIGTERM))
        else:
            os.killpg(group, signal.SIGHUP)
    except (ProcessLookupError, PermissionError, OSError):
        pass
