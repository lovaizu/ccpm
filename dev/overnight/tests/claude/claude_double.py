"""The double of `claude` that overnight's unit cases put on the PATH in its place. It answers each
run, in turn, from one line of a record in recorded/: Claude Code 2.1.332's runs of `claude -p
--output-format json` that end with no error, first and by `--resume`, and one that resumes a
conversation that isn't there; and, of Claude Code's result form and its message, a run stopped by
the usage limit, with exit 1 and with exit 0; as the plugin guide's Each result of a double from a
record says. A run past the answers it was given fails with exit 1, naming itself, so that a body
that runs claude once too often shows it.

A case makes it by `Double(folder)`, gives it the answers by `answer`, and reads each run it was
asked by `calls`. It keeps its state in the folder, which the environment variable
OVERNIGHT_CLAUDE_DOUBLE names to each run."""

from __future__ import annotations

import functools
import json
import os
import signal
import sys
import time
from typing import Any

RECORDED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recorded")
RECORDS = ("claude-2.1.332.jsonl", "claude-manual.jsonl")
# The answers the double gives, by the start of each record's event.
DONE = "done: the work's first run ends with no error"
RESUMED = "done: a run that goes on in the same conversation by --resume ends with no error"
NO_CONVERSATION = "stopped: --resume names a conversation that isn't there"
LIMIT = "stopped: the usage limit, exit 1"
LIMIT_EXIT_0 = "stopped: the usage limit, exit 0"
# Not a record: the run is killed by a signal, as the system does to a process it stops, so that
# claude gives no word.
KILLED = "killed"
# The conversation that every record's run went on in.
SESSION_ID = "6b538ff6-84dd-497c-9d36-7d705fb56125"
# The result that the records of the usage limit hold.
LIMIT_TEXT = "You've hit your limit · resets 4am (Asia/Tokyo)"
NO_CONVERSATION_TEXT = "No conversation found with session ID: 00000000-0000-4000-8000-000000000000"
# The variable that names the double's folder to each run.
FOLDER = "OVERNIGHT_CLAUDE_DOUBLE"
_ANSWERS = "answers.json"
_CALLS = "calls.jsonl"
# The file that a run waits for before it answers, where a case asks it to hold.
_HOLD = "hold"


@functools.lru_cache(maxsize=None)
def _events() -> dict[str, dict[str, Any]]:
    events: dict[str, dict[str, Any]] = {}
    for record in RECORDS:
        with open(os.path.join(RECORDED, record), encoding="utf-8") as f:
            for line in f:
                event = json.loads(line)
                events[event["event"]] = event
    return events


class Double:
    """The double in `folder`, with the `claude` that runs it in `folder`/bin, which `path` gives
    to put first on the PATH."""

    def __init__(self, folder: str) -> None:
        self.folder = folder
        self.path = os.path.join(folder, "bin")
        os.makedirs(self.path)
        claude = os.path.join(self.path, "claude")
        with open(claude, "w", encoding="utf-8") as f:
            f.write(f'#!/bin/sh\nexec "{sys.executable}" "{os.path.abspath(__file__)}" "$@"\n')
        os.chmod(claude, 0o755)
        self.answer()

    def answer(self, *events: str, hold: bool = False) -> None:
        """Has the next runs answer with `events`, one each, in order. With `hold`, each run waits
        until `release` before it answers."""
        with open(os.path.join(self.folder, _ANSWERS), "w", encoding="utf-8") as f:
            json.dump({"events": list(events), "hold": hold}, f)

    def release(self) -> None:
        """Lets each run that holds answer."""
        with open(os.path.join(self.folder, _HOLD), "w", encoding="utf-8"):
            pass

    def calls(self) -> list[dict[str, Any]]:
        """Each run it was asked, in order: its `args`, its `stdin`, its `cwd`, and its `sid`, the
        session of processes it ran in."""
        path = os.path.join(self.folder, _CALLS)
        if not os.path.exists(path):
            return []
        with open(path, encoding="utf-8") as f:
            return [json.loads(line) for line in f]


def _run(folder: str) -> int:
    call = {
        "args": sys.argv[1:],
        "stdin": sys.stdin.read(),
        "cwd": os.getcwd(),
        "sid": os.getsid(0),
    }
    with open(os.path.join(folder, _ANSWERS), encoding="utf-8") as f:
        answers = json.load(f)
    calls = os.path.join(folder, _CALLS)
    count = 0
    if os.path.exists(calls):
        with open(calls, encoding="utf-8") as f:
            count = len(f.readlines())
    with open(calls, "a", encoding="utf-8") as f:
        f.write(json.dumps(call) + "\n")
    if count >= len(answers["events"]):
        sys.stderr.write(f"claude double: no answer for run {count + 1}\n")
        return 1
    while answers["hold"] and not os.path.exists(os.path.join(folder, _HOLD)):
        time.sleep(0.05)
    name = answers["events"][count]
    if name == KILLED:
        os.kill(os.getpid(), signal.SIGKILL)
    event = _events()[name]
    sys.stdout.write(event["stdout"])
    sys.stderr.write(event["stderr"])
    return event["exit"]


if __name__ == "__main__":
    sys.exit(_run(os.environ[FOLDER]))
