"""What every plugin's tests stand on: a temporary folder each test runs in, with its files written
and read; for a test that reads git, a repository made once a run and copied into each test's
folder, git reading no setting of the machine it runs on, since a repository made by git commands
for every test spends most of the tests' time; and, for a plugin whose lanes lane laid, lane's code
as the plugin takes it through a link, and each lane its hooks/lanes.json lays; and, for an
architecture test, a double of Claude Code that sends the hook events and calls the hooks' entries
and the plugins' scripts in the test's own process, kept once as dev/plugin-best-practice.md's
Architecture: the parts joined has it. What a run
of a plugin's tests writes is in one folder of its own, `<plugin>/<yyyymmdd>-tests-<random>/` in the
system's temporary folder, as dev/plugin-best-practice.md's Where a plugin writes its files has it,
the plugin's tests being in dev/<plugin>/tests/; and such a folder for what a trial uses only
while it runs."""

from __future__ import annotations

import atexit
import contextlib
import functools
import importlib
import inspect
import io
import json
import os
import re
import runpy
import shlex
import shutil
import signal
import subprocess
import sys
import sysconfig
import tempfile
import time
import traceback
import unittest
import warnings
from collections.abc import Iterator
from typing import Any, Callable
from unittest import mock

# Each repository made this run, by the name it was made under, kept until the run ends.
MADE: dict[str, str] = {}
# The folder of this run of each plugin's tests, by the plugin's name.
RUNS: dict[str, str] = {}


def temporary(plugin: str, name: str) -> str:
    """A new folder of the plugin's, `<plugin>/<yyyymmdd>-<name>-<random>/` in the system's
    temporary folder, for what a test or a trial uses only while it runs, as
    dev/plugin-best-practice.md's Where a plugin writes its files has it."""
    top = os.path.join(tempfile.gettempdir(), plugin)
    os.makedirs(top, exist_ok=True)
    return tempfile.mkdtemp(prefix=time.strftime(f"%Y%m%d-{name}-"), dir=top)


def run_folder(file: str) -> str:
    """The folder of this run of the tests of the plugin the file is a test of, made the first time
    it is asked for and removed when the run ends."""
    # A test lies in dev/<plugin>/tests/, at any depth below it, as unit/ holds each at the path of
    # what it tests.
    place = os.path.abspath(file)
    while os.path.basename(place) != "tests" and place != os.path.dirname(place):
        place = os.path.dirname(place)
    plugin = os.path.basename(os.path.dirname(place))
    if plugin not in RUNS:
        made = temporary(plugin, "tests")
        RUNS[plugin] = os.path.realpath(made)
        atexit.register(shutil.rmtree, made, True)
    return RUNS[plugin]


class FolderTest(unittest.TestCase):
    """Each test runs in a temporary folder of its own, `base`, in the run's folder, removed after
    it."""

    def setUp(self) -> None:
        self.run_folder = run_folder(inspect.getfile(type(self)))
        self.base = os.path.realpath(tempfile.mkdtemp(dir=self.run_folder))
        self.addCleanup(shutil.rmtree, self.base)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.base)

    def write(self, path: str, text: str) -> None:
        """Writes the text at the path, making its folder where it is not there."""
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def write_json(self, path: str, data: Any) -> None:
        """Writes the data at the path as JSON on one line."""
        self.write(path, json.dumps(data))

    def read(self, path: str) -> str:
        """The text at the path."""
        with open(path, encoding="utf-8") as f:
            return f.read()

    def read_json(self, path: str) -> Any:
        """The JSON at the path."""
        with open(path, encoding="utf-8") as f:
            return json.load(f)


class GitTest(FolderTest):
    """A test whose git reads no setting of the machine and finds no repository above `base`."""

    def setUp(self) -> None:
        super().setUp()
        env = {
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "HOME": self.base,
            "GIT_CEILING_DIRECTORIES": self.base,
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@example.com",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@example.com",
        }
        patcher = mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)

    def git(self, *args: str) -> None:
        """Runs git with the arguments where the test stands; fails the test where git fails."""
        subprocess.run(["git", *args], check=True, capture_output=True)

    def commit(self) -> None:
        """Commits every change on the checked-out branch."""
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "c")

    def copied(self, name: str, make: Callable[[], None]) -> str:
        """The repository `make` builds where it stands, made the first time a test asks for it by
        this name and copied into `base/<name>` for each test, which then stands in it."""
        if name not in MADE:
            made = tempfile.mkdtemp(dir=self.run_folder)
            os.chdir(made)
            make()
            MADE[name] = made
        place = os.path.join(self.base, name)
        shutil.copytree(MADE[name], place, symlinks=True)
        os.chdir(place)
        return place


def load_hypothesis_profile() -> None:
    """Loads Hypothesis's settings, once a property test has imported it: new inputs on every run,
    CI included, a failure printing how to reproduce it, nothing kept after the run, its folder in
    the run's folder of the plugin whose module of property tests loads them, and no deadline, as an
    example's time varies from machine to machine; few inputs while a change is made and many in
    CI, the dev and ci profiles of Hypothesis's settings guide."""
    import hypothesis  # pyrefly: ignore[missing-import]
    import hypothesis.configuration  # pyrefly: ignore[missing-import]

    loading = next(f.filename for f in inspect.stack() if f.filename != __file__)
    hypothesis.configuration.set_hypothesis_home_dir(tempfile.mkdtemp(dir=run_folder(loading)))
    kept = {"derandomize": False, "database": None, "print_blob": True, "deadline": None}
    hypothesis.settings.register_profile("dev", max_examples=10, **kept)
    hypothesis.settings.register_profile("ci", max_examples=1000, **kept)
    hypothesis.settings.load_profile("ci" if os.environ.get("CI") else "dev")


def hypothesis() -> Any:
    """Hypothesis, its settings loaded as load_hypothesis_profile says, for a module of property
    tests to take given, assume and strategies from; stops the module, its tests skipped, where it
    is not installed, as it is installed on the newest Python alone, so the type check on 3.9
    finds it missing."""
    try:
        import hypothesis  # pyrefly: ignore[missing-import]
    except ImportError:
        raise unittest.SkipTest("Hypothesis runs on the newest Python alone") from None
    load_hypothesis_profile()
    return hypothesis


# What an Agent call gives back of a run started in the background, as Claude Code 2.1.317 gave it.
LAUNCHED = "async_launched"
# What the double of Claude Code does where the hooks reference says nothing, each as a try of the
# real Claude Code showed it, with the version and the day of the try, as
# dev/plugin-best-practice.md's Where a double's results come from asks. A double that does what
# no try showed passes a test that the real Claude Code fails.
TRIES = [
    {
        "showed": "an Agent call starting a subagent in the background gives SubagentStart of the"
        " run, then PostToolUse of the call within 1 ms, its tool_response holding `status`"
        " `async_launched` and the run's `agentId`",
        "version": "2.1.317",
        "day": "2026-11-03",
    },
    {
        "showed": "a run's first call comes seconds after the PostToolUse of the Agent call that"
        " started it",
        "version": "2.1.317",
        "day": "2026-11-03",
    },
    {
        "showed": "once a subagent started in the background ends, Claude Code starts the subagent"
        " that started it again, sending SubagentStart of the same agent_id, in an interactive"
        " session alone; `claude -p` hands the end to the main conversation instead",
        "version": "2.1.317",
        "day": "2026-11-03",
    },
    {
        "showed": "a Bash command that exits with an error comes back as PostToolUseFailure",
        "version": "not recorded",
        "day": "2026-11-03",
    },
    {
        "showed": "with plugins a and b enabled, each event of b's subagent worker, SubagentStart,"
        " PreToolUse, PostToolUse and SubagentStop, reaches the hooks of both, agent_type"
        " `b:worker` and one agent_id, in the foreground and in the background, whether or not a"
        " declares b in its dependencies; the two plugins' hooks run in either order",
        "version": "2.1.318",
        "day": "2026-11-05",
    },
    {
        "showed": "where both plugins' hooks deny one PreToolUse, the call is denied and the"
        " subagent sees one reason alone, `PreToolUse:Bash hook error: <reason>`; where one denies"
        " and the other allows, the deny holds; where both block one SubagentStop, the subagent"
        " gets both reasons in one message",
        "version": "2.1.318",
        "day": "2026-11-05",
    },
]


# The folders of Python's own modules and of those installed, which a new process of Python finds
# as this one does.
SHARED = tuple(
    os.path.realpath(sysconfig.get_paths()[k]) + os.sep
    for k in ("stdlib", "platstdlib", "purelib", "platlib")
)
# The words of a hook's command after which it runs its entry, as `lay.py write` writes it: the
# entry's path in the plugin's folder, and the words it is given.
ENTRY = re.compile(r'python3 -B "\$\{CLAUDE_PLUGIN_ROOT\}/([^"]+\.py)"([^;&|]*)$')
# What sh reads apart in a command: one with any of them runs in sh.
SH = set("$`\\;&|<>()*?[]{}~#!\n")


class Late(BaseException):
    """A call still running at its timeout, raised in it as an error the code it runs does not
    catch."""


@functools.cache
def shared_file(file: str) -> bool:
    """Whether the file lies in a folder of Python's own modules or of those installed."""
    return os.path.realpath(file).startswith(SHARED)


def shared(module: Any) -> bool:
    """Whether the module is one a new process of Python shares with this one: built in, or
    Python's own or installed; not a module of a plugin's, of the tests', or a namespace package
    that could be either."""
    file = getattr(module, "__file__", None)
    if file is None:
        return not hasattr(module, "__path__")
    return shared_file(file)


@functools.cache
def fresh_path() -> list[str]:
    """sys.path of a new process of Python, beside the folder of the script it runs, as this
    process's environment gives it."""
    done = subprocess.run(
        [sys.executable, "-c", "import json, sys; print(json.dumps(sys.path[1:]))"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(done.stdout)


@contextlib.contextmanager
def within(seconds: float | None) -> Iterator[None]:
    """Raises Late in what runs inside where it runs past the seconds, as Claude Code stops a hook
    at its timeout; no limit where None."""
    if seconds is None:
        yield
        return

    def late(signum: int, frame: Any) -> None:
        raise Late

    before = signal.signal(signal.SIGALRM, late)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, before)


def exit_code(code: Any, stderr: io.StringIO) -> int:
    """The exit code of a script ended by SystemExit with the code, as Python gives it: 0 for None,
    the number, or 1 with anything else written on stderr."""
    if code is None:
        return 0
    if isinstance(code, int):
        return code
    stderr.write(f"{code}\n")
    return 1


def inside(
    path: str,
    argv: list[str],
    stdin: str,
    env: dict[str, str],
    cwd: str,
    seconds: float | None = None,
    bytecode: bool = True,
) -> tuple[int, str, str]:
    """The exit code, the stdout and the stderr of the Python script at the path, run in this
    process as `python3 <path> <argv>` runs it in a new one: as `__main__`, given the text on
    stdin, in the folder cwd and the environment env, its own folder first on sys.path and
    Python's warnings as a new process has them, writing compiled files only where `bytecode`;
    stopped by AssertionError where it still runs after the seconds. A new process shares no
    module with another but Python's own and those installed, so the script imports every other
    afresh, and none of this process's, such as a module of another plugin's of the same name,
    reaches it; what it changes of this process is put back after."""
    modules = dict(sys.modules)
    kept = (list(sys.path), list(sys.argv), dict(os.environ), os.getcwd())
    streams = (sys.stdin, sys.stdout, sys.stderr)
    held = (tempfile.tempdir, sys.dont_write_bytecode)
    stdout, stderr = io.StringIO(), io.StringIO()
    for name, module in modules.items():
        if not shared(module):
            del sys.modules[name]
    sys.path[:] = [os.path.dirname(path), *fresh_path()]
    sys.argv[:] = [path, *argv]
    os.environ.clear()
    os.environ.update(env)
    # Each reads the environment once, so is made to read the call's.
    tempfile.tempdir = None
    sys.dont_write_bytecode = not bytecode
    sys.stdin, sys.stdout, sys.stderr = io.StringIO(stdin), stdout, stderr
    importlib.invalidate_caches()
    code = 0
    try:
        os.chdir(cwd)
        with warnings.catch_warnings(), within(seconds):
            warnings.resetwarnings()
            warnings.filterwarnings("default", category=DeprecationWarning, module="__main__")
            for kind in (DeprecationWarning, PendingDeprecationWarning, ImportWarning):
                warnings.filterwarnings("ignore", category=kind)
            warnings.filterwarnings("ignore", category=ResourceWarning)
            runpy.run_path(path, run_name="__main__")
    except SystemExit as stop:
        code = exit_code(stop.code, stderr)
    except Late:
        raise AssertionError(f"{path} did not end within {seconds} seconds") from None
    # An error the script does not catch ends a new process with its traceback, so ends the call.
    except Exception:  # noqa: BLE001
        stderr.write(traceback.format_exc())
        code = 1
    finally:
        for name in [n for n, m in sys.modules.items() if not shared(m)]:
            del sys.modules[name]
        sys.modules.update(modules)
        sys.path[:], sys.argv[:] = kept[0], kept[1]
        os.environ.clear()
        os.environ.update(kept[2])
        os.chdir(kept[3])
        sys.stdin, sys.stdout, sys.stderr = streams
        tempfile.tempdir, sys.dont_write_bytecode = held
    return code, stdout.getvalue(), stderr.getvalue()


class Run:
    """A run of a subagent, as the hooks see it: its type, `<plugin>:<name>`, and its ID."""

    def __init__(self, kind: str, agent_id: str) -> None:
        self.kind = kind
        self.agent_id = agent_id


class Told:
    """What a call or an end came to, as the double of Claude Code saw it: whether it was made, what
    the hooks said of it, and the context the hooks added after it."""

    def __init__(self, made: bool, said: dict[str, Any], context: list[str]) -> None:
        self.made = made
        self.said = said
        self.context = context

    def reason(self) -> str:
        """The reason the hooks gave for a call denied or asked, or for an end blocked."""
        specific = self.said.get("hookSpecificOutput", {})
        return str(specific.get("permissionDecisionReason") or self.said.get("reason") or "")

    def decision(self) -> str:
        """`deny` or `ask` for a call, `block` for an end, or "" where the hooks let it go on."""
        specific = self.said.get("hookSpecificOutput", {})
        return str(specific.get("permissionDecision") or self.said.get("decision") or "")

    def operator(self) -> str:
        """What the hooks told the operator, as Claude Code shows it, the systemMessage."""
        return str(self.said.get("systemMessage", ""))


class ClaudeCode:
    """A double of Claude Code for an architecture test: it sends each hook event in the fields the
    hooks reference documents, calls the entry of each command the hooks/hooks.json of each plugin
    enabled gives the event, as Claude Code merges every plugin's hooks, and acts on what the
    entries print. It calls each entry in the test's own process, as `inside` says, and does not run
    the rest of its command, which checks for Python: the parts are joined in one process, as
    dev/plugin-best-practice.md's Architecture: the parts joined has it, and a configuration file
    such as hooks.json is not tested. A call denied is not made; a call asked of the person is made
    where the person's next set answer is yes; any other is made for real in the folder the session
    works in, and comes back as PostToolUse, or PostToolUseFailure where it failed. An end blocked
    keeps its run going. A hook entry that fails fails the test, as no path through Lane has one
    fail, and so do a hook's command that names no entry as `lay.py write` writes it, and two
    plugins' hooks that both answer one event, as the hooks reference documents no way they
    combine. Where the hooks reference says nothing, it does what TRIES recorded of the real Claude
    Code. Each event it sends of a call, a start or an end is first held to `check`, the part's own
    check of what Claude Code hands it, which gives what is wrong, "" where nothing is."""

    def __init__(
        self,
        root: str,
        cwd: str,
        env: dict[str, str],
        answers: list[bool] | None = None,
        others: tuple[str, ...] = (),
        check: Callable[[dict[str, Any]], str] = lambda event: "",
    ) -> None:
        self.root = root
        self.roots = [root, *others]
        self.cwd = cwd
        self.env = env
        self.answers = list(answers or [])
        self.check = check
        self.uses = 0
        # The runs a stop hook kept going, so their next SubagentStop says so.
        self.kept_going: set[str] = set()

    def common(self, held: str, run: Run | None) -> dict[str, Any]:
        """The fields every event of the name has, of the run, or of the main conversation where
        none is given, as the hooks reference documents them."""
        event: dict[str, Any] = {
            "session_id": "s1",
            "transcript_path": os.path.join(self.cwd, "s1.jsonl"),
            "cwd": self.cwd,
            "permission_mode": "default",
            "hook_event_name": held,
        }
        if run is not None:
            event.update(agent_id=run.agent_id, agent_type=run.kind)
        return event

    def send(self, event: dict[str, Any]) -> dict[str, Any]:
        """What the hook entries of the event print, as JSON, of the one plugin whose hooks answer
        it, each called with that plugin's folder as CLAUDE_PLUGIN_ROOT."""
        said: dict[str, Any] = {}
        for root in self.roots:
            found = self.sent(root, event)
            if found and said:
                raise AssertionError(f"two plugins' hooks answered {event['hook_event_name']}")
            said = found or said
        return said

    def held(self, event: dict[str, Any]) -> dict[str, Any]:
        """The event, held to `check`; fails the test where it is out of what Claude Code
        hands."""
        wrong = self.check(event)
        if wrong:
            raise AssertionError(f"the double made an event Claude Code would not hand: {wrong}")
        return event

    def sent(self, root: str, event: dict[str, Any]) -> dict[str, Any]:
        """What the hook entries of the event in the plugin at root print, as JSON, of each entry
        of hooks.json whose matcher is `*`, or a regular expression on the tool's name or the
        subagent's type: each called as `inside` says, with that plugin's folder as
        CLAUDE_PLUGIN_ROOT, within its timeout; nothing where the plugin has no hooks."""
        held = event["hook_event_name"]
        path = os.path.join(root, "hooks", "hooks.json")
        if not os.path.exists(path):
            return {}
        with open(path, encoding="utf-8") as f:
            entries = json.load(f)["hooks"].get(held, [])
        on = str(event.get("tool_name", event.get("agent_type", "")))
        said: dict[str, Any] = {}
        for entry in entries:
            matcher = entry.get("matcher", "")
            if matcher not in ("", "*") and not re.fullmatch(matcher, on):
                continue
            for h in entry["hooks"]:
                found = ENTRY.search(h["command"])
                if found is None:
                    told = f"the double calls no entry of the command `{h['command']}`"
                    raise AssertionError(told)
                code, out, err = inside(
                    os.path.join(self.cwd, root, found[1]),
                    shlex.split(found[2]),
                    json.dumps(event),
                    {**self.env, "CLAUDE_PLUGIN_ROOT": root},
                    self.cwd,
                    h.get("timeout", 600),
                    bytecode=False,
                )
                if code or err:
                    raise AssertionError(f"the hook of {held} failed: {err}")
                said.update(json.loads(out) if out else {})
        return said

    def call(self, run: Run | None, tool: str, given: dict[str, Any]) -> Told:
        """A tool call of the run, or of the main conversation, with its input: PreToolUse, then,
        where the hooks let it go on or the person says yes, the call made and PostToolUse or
        PostToolUseFailure."""
        self.uses += 1
        use = {"tool_name": tool, "tool_input": given, "tool_use_id": f"toolu_{self.uses}"}
        said = self.send(self.held({**self.common("PreToolUse", run), **use}))
        decision = said.get("hookSpecificOutput", {}).get("permissionDecision")
        if decision == "deny" or (decision == "ask" and not self.answers.pop(0)):
            return Told(False, said, [])
        response, error = self.made(tool, given)
        if error is None:
            after = {**self.common("PostToolUse", run), **use, "tool_response": response}
        else:
            failed = {"error": error, "is_interrupt": False}
            after = {**self.common("PostToolUseFailure", run), **use, **failed}
        return Told(True, said, self.context(self.send(self.held(after))))

    def made(self, tool: str, given: dict[str, Any]) -> tuple[Any, str | None]:
        """What the call gives back, made for real in the session's folder: a Bash command that
        runs a script of a plugin enabled called as `inside` says, and any other run in sh; a
        file written, edited or read; and the error where it failed, None where it did not."""
        if tool == "Bash":
            found = self.script(given["command"])
            if found is None:
                done = subprocess.run(
                    ["sh", "-c", given["command"]],
                    capture_output=True,
                    text=True,
                    env=self.env,
                    cwd=self.cwd,
                    check=False,
                )
                code, out, err = done.returncode, done.stdout, done.stderr
            else:
                code, out, err = inside(*found[:2], "", self.env, self.cwd, bytecode=found[2])
            if code:
                return None, f"Exit code {code}\n{err}"
            return {"stdout": out, "stderr": err, "interrupted": False}, None
        path = os.path.join(self.cwd, str(given.get("file_path", "")))
        if tool == "Write":
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(given["content"])
            return {"type": "create", "filePath": path}, None
        if tool == "Edit":
            with open(path, encoding="utf-8") as f:
                text = f.read()
            with open(path, "w", encoding="utf-8") as f:
                f.write(text.replace(given["old_string"], given["new_string"], 1))
            return {"filePath": path}, None
        if tool == "Read":
            with open(path, encoding="utf-8") as f:
                return {"type": "text", "file": {"filePath": path, "content": f.read()}}, None
        return {}, None

    def script(self, command: str) -> tuple[str, list[str], bool] | None:
        """The script of a plugin enabled the command runs, `python3 <script> <words>` or `python3
        -B <script> <words>`, its path from the session's folder or whole: its path, its words and
        whether it may write compiled files; None for any other command, and for one with
        anything sh reads apart, such as a variable, a quote left open or a second command."""
        if SH & set(command):
            return None
        try:
            words = shlex.split(command)
        except ValueError:
            return None
        bytecode = words[1:2] != ["-B"]
        words = words[:1] + words[1 + (not bytecode) :]
        if words[:1] != ["python3"] or len(words) < 2 or not words[1].endswith(".py"):
            return None
        path = os.path.normpath(os.path.join(self.cwd, words[1]))
        if not any(path.startswith(os.path.normpath(r) + os.sep) for r in self.roots):
            return None
        return path, words[2:], bytecode

    def start(
        self,
        by: Run | None,
        run: Run,
        prompt: str,
        meanwhile: Callable[[], object] = lambda: None,
    ) -> Told:
        """An Agent call of the run `by`, or of the main conversation, starting the run in the
        background with the prompt: PreToolUse; where it goes on, SubagentStart of the run, what
        the run does `meanwhile`, before its start comes back, then PostToolUse with the run's ID,
        as the first of TRIES showed; the context the hooks added at either."""
        self.uses += 1
        given = {"description": "d", "prompt": prompt, "subagent_type": run.kind}
        use = {"tool_name": "Agent", "tool_input": given, "tool_use_id": f"toolu_{self.uses}"}
        said = self.send(self.held({**self.common("PreToolUse", by), **use}))
        if said.get("hookSpecificOutput", {}).get("permissionDecision") == "deny":
            return Told(False, said, [])
        started = self.started(run)
        meanwhile()
        back = {"status": LAUNCHED, "agentId": run.agent_id, "content": []}
        after = {**self.common("PostToolUse", by), **use, "tool_response": back}
        return Told(True, said, started + self.context(self.send(self.held(after))))

    def started(self, run: Run) -> list[str]:
        """SubagentStart of the run, as Claude Code sends it as the run starts, and again, of the
        same ID, as the hooks reference documents for a run resumed and as TRIES showed for an
        orchestrator started again once a run it started in the background has ended: the context
        the hooks added."""
        return self.context(self.send(self.held(self.common("SubagentStart", run))))

    def stop(self, run: Run) -> Told:
        """SubagentStop of the run, as it is about to end, `stop_hook_active` where a stop hook kept
        it going before: blocked, the run goes on; let end otherwise."""
        transcript = os.path.join(self.cwd, "s1", "subagents", f"agent-{run.agent_id}.jsonl")
        event = {
            **self.common("SubagentStop", run),
            "stop_hook_active": run.agent_id in self.kept_going,
            "agent_transcript_path": transcript,
            "last_assistant_message": "done",
        }
        said = self.send(self.held(event))
        if said.get("decision") == "block":
            self.kept_going.add(run.agent_id)
            return Told(False, said, [])
        self.kept_going.discard(run.agent_id)
        return Told(True, said, [])

    @staticmethod
    def context(said: dict[str, Any]) -> list[str]:
        """The context the hooks added, as Claude Code gives it to the run."""
        added = said.get("hookSpecificOutput", {}).get("additionalContext")
        return [added] if added else []


def lane_code(plugin: str, *names: str) -> list[Any]:
    """lane's modules of the names, imported from the link in the plugin's hooks, or from lane's
    layer, plugins/lane/scripts/, which reads the plugin's hooks.json as `lay.py` does: lane's code
    and the plugin's scripts share module names, such as call, so lane's are imported apart and the
    plugin's put back after."""
    code = os.path.join(plugin, "hooks", "lane")
    here = os.path.dirname(os.path.abspath(__file__))
    layer = os.path.join(here, "..", "..", "plugins", "lane", "scripts")
    shared = {os.path.splitext(n)[0] for f in (code, layer) for n in os.listdir(f)} & {
        os.path.splitext(n)[0] for n in os.listdir(os.path.join(plugin, "scripts"))
    }
    own = {n: sys.modules.pop(n) for n in shared if n in sys.modules}
    sys.path[:0] = [code, layer]
    try:
        return [importlib.import_module(n) for n in names]
    finally:
        del sys.path[:2]
        for n in shared:
            sys.modules.pop(n, None)
        sys.modules.update(own)
