"""What every plugin's trials stand on: the folder of its own each run of a trial writes in, Claude
Code started on copies of plugins as their user starts it, a conversation gone on with message by
message, its record kept, and what the records of the agents it started show."""

from __future__ import annotations

import glob
import importlib.util
import json
import os
import queue
import subprocess
import sys
import threading
import time
from typing import Any

# The seconds Claude Code is given, after a result, to open a turn of its own; it opens one at once
# for what has already reached it, as its records show, such as an agent's message queued while
# the main conversation worked.
QUIET = 5
HERE = os.path.dirname(os.path.abspath(__file__))
# The folder a trial writes in is made as a test's is, by testing.py, kept in the folder above.
sys.path.insert(0, os.path.dirname(HERE))
import testing

# How Claude Code keeps its records is read by lane's record.py, loaded from its file, so a
# plugin's trials standing on this module meet their own modules of the names lane's code has, such
# as call.
RECORD = os.path.join(HERE, "../../../plugins/lane/hooks/lane/record.py")
FOUND = importlib.util.spec_from_file_location("record", os.path.normpath(RECORD))
assert FOUND and FOUND.loader
record = importlib.util.module_from_spec(FOUND)
FOUND.loader.exec_module(record)


def folder(plugin: str, name: str) -> str:
    """A new folder of the plugin's for a run of the trial of the name, in the system's temporary
    folder as dev/architecture.md's Where a plugin writes its files has it, outside any ccpm clone,
    so the conversations started in it load none of its instructions; its path is printed first,
    for whoever runs the trial to find what the run writes there. The path is given with every link
    in it followed, as Claude Code names the folder of a conversation's records by it, and macOS's
    temporary folder is reached through a link."""
    made = os.path.realpath(testing.temporary(plugin, name))
    print("folder:", made, flush=True)
    return made


class Conversation:
    """One conversation with Claude Code on the copies of plugins in place of the installed ones,
    as their user has it, in one live run of Claude Code: the caller reads each reply of the main
    conversation and, as the user does, either sends the next message or waits for the next reply
    without sending, as where the reply says an agent in the background is still at work; a fresh
    conversation is another Conversation. The run starts at the first message and ends on close.
    wait is the minutes a wait for a reply is given, and a wait for the agents in the background
    where send waits for them, 10 where it is 0, as Claude Code waits when given one prompt; env
    is set over the environment Claude Code runs in."""

    def __init__(
        self,
        plugins: list[str],
        cwd: str | None = None,
        wait: int = 0,
        env: dict[str, str] | None = None,
    ) -> None:
        self.plugins, self.cwd, self.env = plugins, cwd, {**os.environ, **(env or {})}
        self.wait = (wait or 10) * 60
        self.run: subprocess.Popen[str] | None = None
        # Whether an agent it started in the background still runs, kept from reply to reply, as
        # Claude Code lists the agents running only when the list changes; a caller that cannot
        # read a reply, as a script cannot, waits for the next while one runs.
        self.running = False
        self.printed: queue.Queue[str | None] = queue.Queue()
        self.errors: list[str] = []

    def start(self) -> subprocess.Popen[str]:
        """Starts Claude Code, reading each message as a line of stream-json from its input and
        printing what it does as stream-json; a thread hands on each line it prints, and None once
        it has ended, and another keeps what it prints as errors."""
        names = []
        for plugin in self.plugins:
            with open(os.path.join(plugin, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
                names.append(json.load(f)["name"])
        command = ["claude", "-p", "--input-format", "stream-json"]
        command += ["--output-format", "stream-json", "--verbose"]
        for plugin in self.plugins:
            command += ["--plugin-dir", plugin]
        # The copy stands in for the installed plugin, which would otherwise run beside it.
        installed = {f"{name}@ccpm": False for name in names}
        command += ["--model", "opus", "--settings", json.dumps({"enabledPlugins": installed})]
        command += ["--permission-mode", "bypassPermissions"]
        run = subprocess.Popen(
            command,
            cwd=self.cwd,
            env=self.env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )

        def hand_on() -> None:
            assert run.stdout
            for line in run.stdout:
                self.printed.put(line)
            self.printed.put(None)

        threading.Thread(target=hand_on, daemon=True).start()
        threading.Thread(target=self.errors.extend, args=(run.stderr,), daemon=True).start()
        return run

    def send(self, prompt: str, record: str | None = None, idle: bool = False) -> dict[str, Any]:
        """Sends prompt and gives the main conversation's reply, as reply does, the turn for the
        message being open at once; where idle, the reply after which no agent runs in the
        background either, as Claude Code waits for them when given one prompt."""
        self.run = self.run or self.start()
        assert self.run.stdin
        message = {"type": "user", "message": {"role": "user", "content": prompt}}
        self.run.stdin.write(json.dumps(message) + "\n")
        self.run.stdin.flush()
        return self.read(record, True, idle)

    def reply(self, record: str | None = None) -> dict[str, Any]:
        """Sends nothing and gives the main conversation's next reply, as the user waits for it
        where the last asked them nothing: Claude Code opens a turn of its own when an agent in the
        background ends or sends it a message. Stops where no turn opens within the wait."""
        return self.read(record, False, False)

    def read(self, record: str | None, due: bool, idle: bool) -> dict[str, Any]:
        """Reads what Claude Code prints until the main conversation has replied, and gives its
        result, the last line Claude Code printed for it as stream-json, such as its session_id;
        due is whether a turn is to open at once, as for a message sent, and idle is send's. Given
        record, it adds there each line as it comes, kept before a failed run stops the trial.
        Stops where Claude Code ends, gives a result that is an error, opens no turn within the
        wait where none is due, or, where idle, still has an agent running the wait after the
        reply."""
        # Claude Code gives a result at the end of each of its turns, and opens a new turn, by an
        # init, for a message sent and on its own for an agent in the background that ends or
        # sends the main conversation a message; meanwhile it prints what those agents do, and
        # lists the agents running each time the list changes. The main conversation has replied
        # at a result after which no turn opens in QUIET seconds, whatever the agents print.
        assert self.run
        result: dict[str, Any] | None = None
        opened, since = due, time.monotonic()
        # The end of the wait: for a reply where none is due, and where idle for the agents, from
        # the first result.
        until = None if due else since + self.wait
        with open(record or os.devnull, "a", encoding="utf-8") as kept:
            while True:
                if opened:
                    left: float | None = None
                elif result and not (idle and self.running):
                    left = max(0, since + QUIET - time.monotonic())
                else:
                    assert until is not None
                    left = max(0, until - time.monotonic())
                try:
                    line = self.printed.get(timeout=left)
                except queue.Empty:
                    if result and not (idle and self.running):
                        return result
                    if result:
                        raise SystemExit(
                            f"agents in the background still running {self.wait // 60} minutes"
                            " after the reply; give a longer wait"
                        ) from None
                    raise SystemExit(
                        f"no reply in {self.wait // 60} minutes of waiting; give a longer wait"
                    ) from None
                if line is None:
                    code = self.run.wait()
                    raise SystemExit(f"claude exited {code}: {''.join(self.errors)}")
                kept.write(line)
                kept.flush()
                event = json.loads(line)
                if event.get("subtype") == "background_tasks_changed":
                    self.running = bool(event.get("tasks"))
                    since = time.monotonic() if idle else since
                elif event.get("subtype") == "init":
                    result, opened = None, True
                elif event.get("type") == "result":
                    if event.get("is_error"):
                        raise SystemExit(f"claude gave an error: {event.get('result')}")
                    result, opened, since = event, False, time.monotonic()
                    until = until or since + self.wait

    def close(self) -> None:
        """Ends the conversation's run of Claude Code, where it started one."""
        if self.run:
            assert self.run.stdin
            self.run.stdin.close()
            self.run.wait()
            self.run = None


def claude(
    prompt: str,
    plugins: list[str],
    cwd: str | None = None,
    wait: int = 0,
    record: str | None = None,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Runs a fresh conversation of the one message prompt, as Conversation and its send have it,
    and gives its result once no agent runs in the background, as Claude Code given one prompt
    does."""
    conversation = Conversation(plugins, cwd, wait, env)
    try:
        return conversation.send(prompt, record, idle=True)
    finally:
        conversation.close()


def agents(session: str) -> list[str]:
    """The path of the record of each agent the session started."""
    return glob.glob(record.subagent(record.conversation(session), "*"))


def show(path: str) -> None:
    """Prints a record's path and, of what it holds, each message sent, each tool used and each
    hook stop."""
    print("record:", path)
    for entry in record.read(path) or []:
        # Claude Code's copy of each request says again what the agent did.
        if entry.get("type") == "api-request-blob":
            continue
        if isinstance(entry.get("origin"), dict):
            print("  message:", entry["origin"].get("body"))
        if record.told(entry):
            print("  stop:", record.text(entry))
        for part in record.blocks(entry):
            if part.get("type") == "tool_use":
                print("  use:", part["name"], json.dumps(part["input"], ensure_ascii=False))
            elif part.get("type") == "tool_result" and part.get("is_error"):
                print("  stop:", part.get("content"))
