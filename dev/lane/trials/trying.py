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

# The seconds Claude Code is given, after a result with no agent running, to open a turn of its
# own; it opens one at once, as its records show.
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


# What Claude Code writes in the main conversation's record where an agent's message reaches it.
SENT_BY_AGENT = "<agent-message from="


def unanswered(session: str) -> int:
    """The messages agents sent the main conversation of the session that it has not answered with
    one of its own, read from its record: each message queued for it, less each SendMessage it
    sent an agent; read from the record, as Claude Code prints no SendMessage of an agent two
    layers down, such as turn's generator under turn:up. Each message is counted where it is
    queued, as Claude Code queues every one, and one that reaches the conversation while it works
    comes in beside a tool's result, not as a message of its own, as three questions from turn's
    generator in acceptance run 7 did, two of them so."""
    found = glob.glob(record.conversation(session))
    entries = (record.read(found[0]) or []) if found else []
    reached = sum(
        1
        for e in entries
        if e.get("type") == "queue-operation"
        and e.get("operation") == "enqueue"
        and SENT_BY_AGENT in str(e.get("content", ""))
    )
    sent = sum(
        1
        for e in entries
        if e.get("type") == "assistant"
        for part in record.blocks(e)
        if part.get("type") == "tool_use"
        and part.get("name") == "SendMessage"
        and part.get("input", {}).get("to") != "main"
    )
    return max(0, reached - sent)


class Conversation:
    """One conversation with Claude Code on the copies of plugins in place of the installed ones,
    as their user has it, sent its messages one by one in one live run of Claude Code, as the user
    types each where they read the reply before; a fresh conversation is another Conversation. The
    run starts at the first message and ends on close. wait is the
    minutes a message waits for the agents it started in the background, 10 where it is 0, as
    Claude Code waits when given one prompt; env is set over the environment Claude Code runs in."""

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
        # The messages agents sent the main conversation that it has not yet answered with one of
        # its own, as its record shows at its last result, as the next message may bring the answer.
        self.asked = 0
        # Whether an agent it started in the background still runs, kept from message to message,
        # as Claude Code lists the agents running only when the list changes.
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

    def send(self, prompt: str, record: str | None = None) -> dict[str, Any]:
        """Sends prompt and gives its result, the last line Claude Code printed for it as
        stream-json, such as its session_id, once no agent it started in the background is running,
        or once an agent waits on a message the main conversation has not answered, as turn's
        generator waits on the user's answer, which only the next message can bring. Given record,
        it writes there each line Claude Code printed for it as it comes, kept before a failed run
        stops the trial. Stops where Claude Code ends, gives a result that is an error, or still has
        an agent running after the wait, none waiting on the main conversation."""
        self.run = self.run or self.start()
        assert self.run.stdin
        message = {"type": "user", "message": {"role": "user", "content": prompt}}
        self.run.stdin.write(json.dumps(message) + "\n")
        self.run.stdin.flush()
        # Claude Code gives a result at the end of each of its turns, and on its own opens a new
        # turn, by an init, for the end of an agent in the background its last turn was not told
        # of; it lists the agents running each time the list changes. The message is answered at
        # a result after which nothing is running, or what runs waits on the main conversation, and
        # no turn opens in QUIET seconds.
        result: dict[str, Any] | None = None
        until = None
        with open(record or os.devnull, "w", encoding="utf-8") as kept:
            while True:
                if not self.running or self.asked:
                    left: float | None = QUIET if result else None
                else:
                    left = None if until is None else max(0, until - time.monotonic())
                try:
                    line = self.printed.get(timeout=left)
                except queue.Empty:
                    if result and (not self.running or self.asked):
                        return result
                    raise SystemExit(
                        f"agents in the background still running {self.wait // 60} minutes"
                        " after the reply; give a longer wait"
                    ) from None
                if line is None:
                    code = self.run.wait()
                    raise SystemExit(f"claude exited {code}: {''.join(self.errors)}")
                kept.write(line)
                kept.flush()
                event = json.loads(line)
                if event.get("subtype") == "background_tasks_changed":
                    self.running = bool(event.get("tasks"))
                elif event.get("subtype") == "init":
                    result = None
                elif event.get("type") == "result":
                    if event.get("is_error"):
                        raise SystemExit(f"claude gave an error: {event.get('result')}")
                    result, until = event, until or time.monotonic() + self.wait
                    self.asked = unanswered(event["session_id"])

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
    and gives its result."""
    conversation = Conversation(plugins, cwd, wait, env)
    try:
        return conversation.send(prompt, record)
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
