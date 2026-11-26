"""The double of Claude Code that overnight's unit cases run in its place: the input that it gives a
StopFailure hook, the lines that it writes to a session's transcript, and the `claude` command that
the waiter resumes the session with. Each comes from one line of a record in recorded/, as the
plugin guide's Each result of a double from a record says: the hook's input and claude's exit from
Claude Code's documentation, in claude-manual.jsonl, and the transcript's lines from a session of
Claude Code 2.1.332, in claude-2.1.332-transcript.jsonl, with its prompt, folder, and branch
replaced by placeholders.

The `claude` command is a file that `install` writes. Run, it adds to the file that CALLS names in
its environment a line of what it was called with, where, when, and as which process, and exits as
the record says, so that no case reaches the claude that the developer runs."""

from __future__ import annotations

import copy
import functools
import json
import os
import stat
import sys
import time
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
RECORDED = os.path.join(HERE, "recorded")
MANUAL = "claude-manual.jsonl"
TRANSCRIPT = "claude-2.1.332-transcript.jsonl"
STOP_FAILURE = (
    "StopFailure gives the hook the session, its transcript, its folder, and the error rate_limit"
)
OTHER_ERROR = (
    "StopFailure gives the hook an error other than rate_limit, such as authentication_failed"
)
EXITS = "claude -p exits 0 once its run succeeds"
PROMPT = "a prompt that the user typed records the session's permission mode"
COMMAND = "a command that the user ran in the session records no permission mode"
OUTPUT = "the output of a command that the session ran records no permission mode of its own"
# The variable of the double's environment that names the file where it keeps each call.
CALLS = "CLAUDE_DOUBLE_CALLS"
# How long a case waits for the waiter to run the double: far past the interval of a second that the
# cases give, so that only a waiter that never runs it fails the case.
PATIENCE = 30.0


@functools.cache
def _record(record: str) -> list[dict[str, Any]]:
    with open(os.path.join(RECORDED, record), encoding="utf-8") as f:
        return [json.loads(each) for each in f]


def line(record: str, event: str) -> dict[str, Any]:
    """A copy of the line of the record in recorded/ that the event names."""
    return copy.deepcopy(next(each for each in _record(record) if each["event"] == event))


def session_id() -> str:
    """The ID of the recorded session."""
    return str(line(TRANSCRIPT, PROMPT)["line"]["sessionId"])


def stop_failure(transcript: str, cwd: str) -> dict[str, Any]:
    """The input of a StopFailure hook at the usage limit, naming the recorded session, its
    transcript, and the folder it ran in."""
    given = line(MANUAL, STOP_FAILURE)["input"]
    given.update(session_id=session_id(), transcript_path=transcript, cwd=cwd)
    return given


def other_error() -> str:
    """An error of a StopFailure other than rate_limit."""
    return str(line(MANUAL, OTHER_ERROR)["error"])


def exit_code() -> int:
    """The exit of claude -p once its run succeeds."""
    return int(line(MANUAL, EXITS)["exit"])


def _written(record: dict[str, Any]) -> str:
    """The record as Claude Code writes it as a line of the transcript, whole, with the newline
    that ends it."""
    return json.dumps(record, separators=(",", ":")) + "\n"


def prompt(mode: str) -> str:
    """The transcript's line of a prompt that the user typed in the permission mode, whole, with
    the newline that ends it."""
    record = line(TRANSCRIPT, PROMPT)["line"]
    record["permissionMode"] = mode
    return _written(record)


def command() -> str:
    """The transcript's line of a command that the user ran, which records no permission mode,
    whole, with the newline that ends it."""
    return _written(line(TRANSCRIPT, COMMAND)["line"])


def output(text: str) -> str:
    """The transcript's line of the output of a command that the session ran, the output being
    the text, which records no permission mode of its own, whole, with the newline that ends it."""
    record = line(TRANSCRIPT, OUTPUT)["line"]
    record["message"]["content"][0]["content"] = text
    record["toolUseResult"]["stdout"] = text
    return _written(record)


def transcript(folder: str, text: str) -> str:
    """The path of the session's transcript, written in the folder with the text."""
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{session_id()}.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def install(folder: str) -> str:
    """The path of the double's `claude` command, written in the folder."""
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "claude")
    with open(path, "w", encoding="utf-8") as f:
        f.write(
            f"#!{sys.executable}\nimport sys\nsys.path.insert(0, {HERE!r})\n"
            "import claude_double\nclaude_double.answer()\n"
        )
    os.chmod(path, stat.S_IRWXU)
    return path


def called(calls: str) -> list[dict[str, Any]]:
    """Each call of the double kept in the file, once it holds one, as `argv` without the
    command's own path, `cwd`, `at` by the system's clock, and `pid`. Raises TimeoutError where no
    call comes within PATIENCE."""
    deadline = time.monotonic() + PATIENCE
    while not os.path.exists(calls):
        if time.monotonic() > deadline:
            raise TimeoutError(f"claude wasn't called within {PATIENCE} seconds")
        time.sleep(0.05)
    with open(calls, encoding="utf-8") as f:
        return [json.loads(each) for each in f]


def answer() -> None:
    """Runs as `claude`: adds the call to those kept before it, then exits as the record says."""
    call = {"argv": sys.argv[1:], "cwd": os.getcwd(), "at": time.time(), "pid": os.getpid()}
    calls = os.environ[CALLS]
    kept = ""
    if os.path.exists(calls):
        with open(calls, encoding="utf-8") as f:
            kept = f.read()
    # The calls are written whole and then named, so that a case never reads half of one.
    with open(f"{calls}.part", "w", encoding="utf-8") as f:
        f.write(kept + json.dumps(call) + "\n")
    os.replace(f"{calls}.part", calls)
    raise SystemExit(exit_code())
