"""What overnight's cases share: the README walkthrough's queue, prompts, replies, and texts; a
bench of the user's folders, as `/home/dev` holds them in the walkthrough; the double of the
computer's clock; and the moves of a run as overnight's architecture draws them under Sequences,
each a handoff between overnight's scripts.

Each move runs the `main` of a script's part, `stacker.command`, `runner.command`, and
`checker.command`, as `queue.py` runs it, and feeds what one gives to the next, in the case's own
process, so that the doubles reach each part: the double of Claude Code in place of
`session.claude.claude`, and that of the clock in place of `runner.clock`, the one place where each
goes, as their modules say. So the bench takes a runner that carries its tasks in threads of its
own process. In place of starting the runner apart, the bench keeps what `stacker.detach` would put
on its standard input, which `run` hands `runner.command.main`. `Detached` runs the stacker and the
runner as programs of their own, with the double of Claude Code on the PATH and the computer's own
clock. Each helper plays one move, and says nothing of how overnight's parts carry it."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from collections.abc import Callable, Generator
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Any, NamedTuple

import claude_double
from claude_double import Answer

if TYPE_CHECKING:
    from runner.handoff import Handoff
    from stacker.queue_file import Queue

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PLUGIN = os.path.join(TOP, "plugins", "overnight")
DOMAIN = os.path.join(PLUGIN, "domain")
QUEUE_PY = os.path.join(PLUGIN, "scripts", "queue.py")
VERSION = "0.1.0"
# The day the walkthrough's queue is stacked on.
DAY = date(2026, 11, 24)


def at(hour: int, minute: int, days: int = 0) -> datetime:
    """The moment of the walkthrough's night at the hour on the computer's clock, with its offset
    from UTC, `days` after the day it's stacked on."""
    return datetime(DAY.year, DAY.month, DAY.day, hour, minute).astimezone() + timedelta(days=days)


STACKED = at(22, 30)
START = at(23, 0)
REFUNDS_ENDED = at(23, 52)
FIX_ENDED = at(0, 28, 1)
STOPPED = at(0, 41, 1)
RESET = at(1, 40, 1)
WENT_ON = at(1, 42, 1)
PAYMENTS_ENDED = at(2, 16, 1)

PAYMENTS_PROMPT = (
    "Review the payment module, payments/, for faults. Name each by its file and line."
)
REFUNDS_PROMPT = "Review the refund module, refunds/, for faults. Name each by its file and line."
FIX_PROMPT = (
    "The test tests/test_checkout.py::test_total fails about one run in five. Find why, and fix"
    " the\ncode. Then run the test 20 times, and show that it passes each time. In your reply,"
    " say what\ncaused it and what you changed.\n"
)
BEFORE_THE_LIMIT = (
    "## The checks of a card payment\n\n"
    "payments/card.py:88 retries a declined card without a limit, so one declined card can be"
    " charged\nagain and again."
)
AFTER_THE_LIMIT = (
    "## The checks of a refund to a card\n\n"
    "payments/card.py:140 refunds the whole charge where the request names a part, so a partial"
    " refund\npays back too much."
)
WAIT_LINE = "(The usage limit stopped this task at 00:41. It went on at 01:42.)"
REFUNDS_REPLY = "## The checks of a refund\n\nrefunds/policy.py holds no fault that a review finds."
FIX_REPLY = "A cache shared between tests caused the failure. The test passed 20 times."
# The session of each of the walkthrough's tasks, as the record that its runner leaves holds it.
PAYMENTS_SESSION = "1b4e28ba-2fa1-4d3b-a3f5-ef19ae0f1a01"
REFUNDS_SESSION = "2c5f39cb-3a01-4e4c-b4a6-fa2a0b2b1b02"
FIX_SESSION = "3d6a4adc-4b12-4f5d-b5b7-0b3b3c2c2c03"
# What `/overnight:check` shows where it names no queue that was stacked.
UNNAMED = f"overnight {VERSION}: name the queue file to check"


class Ran(NamedTuple):
    """What a script's part gave: its exit code, its stdout, and its stderr."""

    code: int
    out: str
    err: str


class Clock:
    """The double of the computer's clock. Each thread reads its own moment, which starts at the
    moment the latest wait of any thread ended at, or the bench's start, and moves on as the thread
    waits and as the double of Claude Code ends a run at the moment its case scripted. It keeps each
    wait, and calls each probe at its start, so that a case reads the record while a task waits."""

    def __init__(self, start: datetime):
        self.base = start
        self.waits: list[datetime] = []
        self.probes: list[Callable[[datetime], None]] = []
        self._own = threading.local()
        self._lock = threading.Lock()

    def now(self) -> datetime:
        return getattr(self._own, "at", None) or self.base

    def sleep_until(self, moment: datetime) -> None:
        assert moment.tzinfo is not None, "a moment with no offset from UTC"
        with self._lock:
            self.waits.append(moment)
        for probe in self.probes:
            probe(moment)
        self.passes_to(moment)
        with self._lock:
            self.base = max(self.base, self.now())

    def passes_to(self, moment: datetime) -> None:
        self._own.at = max(self.now(), moment)


@dataclass
class Home:
    """The user's folders, `home` standing for `/home/dev`, and the folder of the double of Claude
    Code's state, as both benches hold them, with what a case writes there and reads back."""

    home: str
    claude: str

    def path(self, *parts: str) -> str:
        """The absolute path under the user's home."""
        return os.path.join(self.home, *parts)

    @property
    def queue_file(self) -> str:
        """The walkthrough's queue file, `/home/dev/overnight/tonight.json`."""
        return self.path("overnight", "tonight.json")

    @property
    def folder(self) -> str:
        """What overnight writes for the walkthrough's queue, `/home/dev/overnight/tonight/`."""
        return self.path("overnight", "tonight")

    def write(self, path: str, text: str) -> str:
        """Writes the file under the user's home, its folders made, and gives its absolute path."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def queue(self, queue: dict[str, Any], path: str | None = None) -> str:
        """Writes the queue as the user writes it in its JSON file, by default the walkthrough's."""
        return self.write(path or self.queue_file, json.dumps(queue, indent=2))

    def script(self, prompt: str, *answers: Answer) -> None:
        """Sets what the sessions of the task of the prompt do, run by run."""
        claude_double.script(self.claude, prompt, *answers)

    def runs(self, folder: str | None = None) -> list[dict[str, Any]]:
        """Each task with its run, as `runs.json` holds them."""
        with open(os.path.join(folder or self.folder, "runs.json"), encoding="utf-8") as f:
            return json.load(f)["tasks"]

    def run_of(self, name: str, folder: str | None = None) -> dict[str, Any]:
        """The run of the task by its name, as `runs.json` holds it."""
        return next(each["run"] for each in self.runs(folder) if each["task"]["name"] == name)

    def reply(self, name: str, folder: str | None = None) -> str:
        """The text of the task's reply file."""
        with open(os.path.join(folder or self.folder, f"{name}.md"), encoding="utf-8") as f:
            return f.read()

    def asked(self) -> list[claude_double.Asked]:
        """Each run of `claude` that the double was asked."""
        return claude_double.asked(self.claude)


@dataclass
class Bench(Home):
    """The user's folders, with the clock's double, each handoff that the stacker gave its runner,
    whether the computer's sandbox runs, and what to call before each run of `claude`."""

    clock: Clock
    handed: list[str] = field(default_factory=list)
    sandbox: list[bool] = field(default_factory=lambda: [True])
    before_claude: list[Callable[[], None]] = field(default_factory=list)

    def stack(self, path: str | None = None) -> Ran:
        """`/overnight:stack` with the queue file, as the skill runs `queue.py stack`."""
        from stacker import command

        return Ran(*command.main([path or self.queue_file], self.home))

    def run(self) -> Ran:
        """The runner that the latest stacking started, fed what the stacker handed it."""
        from runner import command

        return Ran(*command.main([], self.handed.pop()))

    def check(self, *argv: str) -> Ran:
        """`/overnight:check` with the arguments, as the skill runs `queue.py check`."""
        from checker import command

        return Ran(*command.main(list(argv), self.home, PLUGIN))


def bench(tmp: str, monkeypatch: Any, start: datetime = STACKED) -> Bench:
    """A bench in the folder, with the doubles of Claude Code and the clock in their places, the
    runner kept in place of being started, and a computer whose sandbox runs, until the case says
    it doesn't."""
    from runner import clock as clock_module
    from runner import handoff
    from session import claude, sandbox
    from stacker import detach

    the = Bench(os.path.join(tmp, "home", "dev"), os.path.join(tmp, "claude"), Clock(start))
    os.makedirs(the.home)
    double = claude_double.function(the.claude, the.clock, the.before_claude)
    monkeypatch.setattr(claude, "claude", double)
    monkeypatch.setattr(clock_module, "now", the.clock.now)
    monkeypatch.setattr(clock_module, "sleep_until", the.clock.sleep_until)
    monkeypatch.setattr(detach, "start_runner", lambda h: the.handed.append(handoff.encode(h)))
    monkeypatch.setattr(sandbox, "can_hold", lambda: the.sandbox[0])
    return the


def no_sandbox(b: Bench) -> None:
    """Makes the bench's computer one where Claude Code's sandbox can't run, such as Windows
    outside WSL2."""
    b.sandbox[0] = False
    claude_double.no_sandbox(b.claude)


def walkthrough(b: Bench, start: str | None = "23:00") -> str:
    """Writes the walkthrough's prompts, its two folders of work, and its queue file, and gives the
    queue file's path."""
    for name, text in (
        ("review-payments", PAYMENTS_PROMPT),
        ("review-refunds", REFUNDS_PROMPT),
        ("fix-flaky-checkout", FIX_PROMPT),
    ):
        b.write(b.path("overnight", f"{name}.md"), text)
    for folder in ("shop", "shop-fix-flaky-checkout"):
        b.write(b.path("work", folder, "shop", "checkout.py"), "PRICES = {}\n")
    queue: dict[str, Any] = {
        "tasks": [
            {
                "name": "review-payments",
                "prompt": "review-payments.md",
                "dir": b.path("work", "shop"),
            },
            {
                "name": "review-refunds",
                "prompt": "review-refunds.md",
                "dir": b.path("work", "shop"),
            },
            {
                "name": "fix-flaky-checkout",
                "prompt": "fix-flaky-checkout.md",
                "dir": b.path("work", "shop-fix-flaky-checkout"),
                "writes": True,
            },
        ]
    }
    if start is not None:
        queue = {"start": start, **queue}
    return b.queue(queue)


def one_review(b: Bench) -> str:
    """Writes a queue file of the review of the payments alone, with no start, and gives its
    path."""
    task = {
        "name": "review-payments",
        "prompt": "review-payments.md",
        "dir": b.path("work", "shop"),
    }
    return b.queue({"tasks": [task]})


def walkthrough_night(b: Bench) -> None:
    """Scripts the walkthrough's night: the review of the refunds finishes at 23:52, the fix at
    00:28, editing its folder's code and running its test, and the review of the payments reaches
    the usage limit at 00:41, which resets at 01:40, and finishes at 02:16."""
    fixed = b.path("work", "shop-fix-flaky-checkout", "shop", "checkout.py")
    b.script(
        PAYMENTS_PROMPT,
        claude_double.limited(BEFORE_THE_LIMIT, STOPPED, RESET),
        claude_double.finished(AFTER_THE_LIMIT, PAYMENTS_ENDED),
    )
    b.script(REFUNDS_PROMPT, claude_double.finished(REFUNDS_REPLY, REFUNDS_ENDED))
    uses = (
        claude_double.Use("Read", fixed),
        claude_double.Use("Edit", fixed),
        claude_double.Use("Bash", command="pytest tests/test_checkout.py::test_total --count 20"),
    )
    b.script(FIX_PROMPT, claude_double.finished(FIX_REPLY, FIX_ENDED, uses=uses))


def stacked_text(queue_file: str) -> str:
    """What `/overnight:stack` shows for the walkthrough's queue, as the README shows it."""
    return (
        f"Stacked 3 tasks from {queue_file}.\n"
        "They start at 23:00, three at a time, and go on after this session ends.\n"
        f"/overnight:check {queue_file} shows where they stand.\n"
    )


def checked_text(b: Bench) -> str:
    """What `/overnight:check` shows the next morning, as the README shows it."""
    return (
        f"3 tasks from {b.queue_file}: 3 finished, 0 given up.\n"
        "- review-refunds: finished at 23:52.\n"
        f"  Reply: {os.path.join(b.folder, 'review-refunds.md')}\n"
        "- fix-flaky-checkout: finished at 00:28.\n"
        f"  Reply: {os.path.join(b.folder, 'fix-flaky-checkout.md')}\n"
        f"  Wrote in: {b.path('work', 'shop-fix-flaky-checkout')}\n"
        "- review-payments: finished at 02:16, after waiting for the usage limit from 00:41 to"
        " 01:42.\n"
        f"  Reply: {os.path.join(b.folder, 'review-payments.md')}\n"
    )


def payments_reply() -> str:
    """The reply of the review that waited, as the README shows it: its work from before the limit
    and after it, with the line between them."""
    return f"{BEFORE_THE_LIMIT}\n\n{WAIT_LINE}\n\n{AFTER_THE_LIMIT}"


def task_json(name: str, prompt: str, folder: str, writes: bool = False) -> dict[str, Any]:
    """A stacked task, as `runs.json` holds it."""
    return {"name": name, "prompt": prompt, "dir": folder, "writes": writes}


def run_json(state: str, **given: Any) -> dict[str, Any]:
    """A run, as `runs.json` holds it: its state, its stops, and its waits, by default none, and
    each other field given, each moment as ISO 8601."""
    run: dict[str, Any] = {"state": state, "stops": 0, "waits": []}
    for name, value in given.items():
        run[name] = value.isoformat() if isinstance(value, datetime) else value
    return run


def wait_json(stopped: datetime, went_on: datetime | None = None) -> dict[str, str]:
    """A wait for the usage limit, as `runs.json` holds it."""
    wait = {"stopped": stopped.isoformat()}
    if went_on is not None:
        wait["went_on"] = went_on.isoformat()
    return wait


def keep(b: Bench, tasks: list[tuple[dict[str, Any], dict[str, Any]]], folder: str | None = None):
    """Writes the queue's `runs.json` as overnight leaves it, each task with its run."""
    entries = [{"task": task, "run": run} for task, run in tasks]
    b.write(os.path.join(folder or b.folder, "runs.json"), json.dumps({"tasks": entries}))


def walkthrough_tasks(b: Bench) -> list[dict[str, Any]]:
    """The walkthrough's three tasks, as `runs.json` holds them."""
    return [
        task_json(
            "review-payments", b.path("overnight", "review-payments.md"), b.path("work", "shop")
        ),
        task_json(
            "review-refunds", b.path("overnight", "review-refunds.md"), b.path("work", "shop")
        ),
        task_json(
            "fix-flaky-checkout",
            b.path("overnight", "fix-flaky-checkout.md"),
            b.path("work", "shop-fix-flaky-checkout"),
            True,
        ),
    ]


def the_morning(b: Bench) -> None:
    """Writes the record as the walkthrough's runner leaves it the next morning: each task finished,
    the review of the payments after its wait, with each reply."""
    payments, refunds, fix = walkthrough_tasks(b)
    keep(
        b,
        [
            (
                payments,
                run_json(
                    "finished",
                    session=PAYMENTS_SESSION,
                    stops=1,
                    waits=[wait_json(STOPPED, WENT_ON)],
                    ended=PAYMENTS_ENDED,
                ),
            ),
            (
                refunds,
                run_json("finished", session=REFUNDS_SESSION, ended=REFUNDS_ENDED),
            ),
            (
                fix,
                run_json("finished", session=FIX_SESSION, ended=FIX_ENDED),
            ),
        ],
    )
    b.write(os.path.join(b.folder, "review-payments.md"), payments_reply())
    b.write(os.path.join(b.folder, "review-refunds.md"), REFUNDS_REPLY)
    b.write(os.path.join(b.folder, "fix-flaky-checkout.md"), FIX_REPLY)


def left_by_a_stop(b: Bench, session: str = PAYMENTS_SESSION) -> None:
    """Writes the record as a runner that stopped left it, with no lock held: the review of the
    payments running in the session, the review of the refunds finished with its reply, and the fix
    not yet started."""
    payments, refunds, fix = walkthrough_tasks(b)
    keep(
        b,
        [
            (payments, run_json("running", session=session)),
            (refunds, run_json("finished", session=REFUNDS_SESSION, ended=REFUNDS_ENDED)),
            (fix, run_json("waiting for the start")),
        ],
    )
    b.write(os.path.join(b.folder, "review-refunds.md"), REFUNDS_REPLY)


def walkthrough_queue(b: Bench) -> Queue:
    """The walkthrough's queue, as the stacker reads it from its queue file."""
    from stacker.queue_file import Queue, Task

    tasks = tuple(Task(**each) for each in walkthrough_tasks(b))
    return Queue(b.queue_file, "23:00", tasks)


@contextmanager
def held_by_another(hold: str) -> Generator[subprocess.Popen[str], None, None]:
    """Another program, of a process group of its own, holding a lock by `hold`, a call of
    `record.lock` or `record.store`, such as `lock.hold('/home/dev/overnight/tonight/runner.lock')`,
    until the block ends or the program is killed."""
    code = (
        "import sys\n"
        f"sys.path.insert(0, {DOMAIN!r})\n"
        "from record import lock, store\n"
        f"with {hold}:\n"
        "    print('held', flush=True)\n"
        "    sys.stdin.read()\n"
    )
    holder = subprocess.Popen(
        [sys.executable, "-c", code],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    assert holder.stdout is not None and holder.stdin is not None
    if holder.stdout.readline() != "held\n":
        _, said = holder.communicate()
        raise AssertionError(f"no program holds the lock: {said.strip()}")
    try:
        yield holder
    finally:
        if holder.poll() is None:
            holder.stdin.close()
            holder.wait(timeout=30)


def held_elsewhere(queue_file: str) -> AbstractContextManager[subprocess.Popen[str]]:
    """The queue's lock held by another program, as a runner that still carries the queue holds it,
    until the block ends."""
    return held_by_another(f"store.hold({queue_file!r})")


def until(done: Callable[[], bool], seconds: float = 60.0) -> bool:
    """Whether `done` comes true within the seconds, asked again every tenth of a second."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if done():
            return True
        time.sleep(0.1)
    return done()


def moment(text: str) -> datetime:
    """The moment that an ISO 8601 text of `runs.json` gives, `Z` among the forms of UTC."""
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


# The environment variable by which `Detached.stack` starts the runner as a child of the stacking
# session, where the fixture `broken` takes out the part that keeps it apart.
ATTACHED = "OVERNIGHT_TEST_RUNNER_ATTACHED"


@dataclass
class Detached(Home):
    """The user's folders, with the double of Claude Code written as the program `claude` in `bin`,
    first on the PATH of each program that a stacking session starts, for a runner that runs apart
    on the computer's own clock."""

    bin: str

    def env(self) -> dict[str, str]:
        """The environment of the stacking session: the double first on its PATH."""
        return dict(os.environ, PATH=self.bin + os.pathsep + os.environ.get("PATH", ""))

    def stack(self, queue_file: str) -> Ran:
        """`/overnight:stack` with the queue file in a stacking session of its own, a process of its
        own group, which then ends, every program left in its group stopped with it, as the end of
        the session that ran the skill stops what it started."""
        code = (
            "import os, subprocess, sys\n"
            f"sys.path.insert(0, {DOMAIN!r})\n"
            f"if os.environ.get({ATTACHED!r}) == '1':\n"
            "    from runner import handoff\n"
            "    from stacker import detach\n"
            "    def attached(given):\n"
            f"        child = subprocess.Popen([sys.executable, {QUEUE_PY!r}, 'run'],"
            " stdin=subprocess.PIPE, text=True)\n"
            "        child.stdin.write(handoff.encode(given))\n"
            "        child.stdin.close()\n"
            "    detach.start_runner = attached\n"
            "from stacker import command\n"
            f"code, out, err = command.main([{queue_file!r}], {self.home!r})\n"
            "sys.stdout.write(out)\n"
            "sys.stderr.write(err)\n"
            "sys.exit(code)\n"
        )
        session = subprocess.Popen(
            [sys.executable, "-c", code],
            cwd=self.home,
            env=self.env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        out, err = session.communicate(timeout=60)
        end_group(session.pid)
        return Ran(session.returncode, out, err)


def detached(tmp: str) -> Detached:
    """A bench for a runner that runs apart, with the double of Claude Code on its PATH."""
    the = Detached(os.path.join(tmp, "home", "dev"), os.path.join(tmp, "claude"), "")
    os.makedirs(the.home)
    the.bin = claude_double.program(os.path.join(tmp, "bin"), the.claude)
    return the


def stacked_review(d: Detached, seconds: float) -> Handoff:
    """Writes a queue of the review of the payments alone, stacked, whose session takes the seconds,
    and gives what its runner is handed."""
    from record import store
    from runner.handoff import Carried, Handoff
    from stacker import queue_file

    os.makedirs(d.path("work"))
    d.write(d.path("review.md"), PAYMENTS_PROMPT)
    path = d.queue(
        {"tasks": [{"name": "review-payments", "prompt": "review.md", "dir": d.path("work")}]},
        d.path("tonight.json"),
    )
    d.script(PAYMENTS_PROMPT, claude_double.finished("reviewed", seconds=seconds))
    queue = queue_file.read(path)
    store.stack(queue)
    return Handoff(path, None, (Carried(queue.tasks[0], None),))


def end_group(pid: int) -> None:
    """Stops each program left in the process group that `pid` leads, as a session's end does."""
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True, check=False)
        return
    import signal

    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
