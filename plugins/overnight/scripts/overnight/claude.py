"""Decides how overnight runs `claude`, the one program outside it that it runs, and how it reads
what a run gave: whether the run is done, and why it stopped."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Sequence
from typing import NamedTuple, Protocol

# What a run of `claude` gave: its exit code, its stdout, and its stderr, as text.
Ran = subprocess.CompletedProcess[str]


class Host(Protocol):
    """A run of `claude` as overnight's code runs it: the command's words, from `claude` on, the
    folder it runs in, and what it reads on stdin, to what it gave. `run` is the real one; a test
    passes a double."""

    def __call__(self, argv: Sequence[str], cwd: str, stdin: str) -> Ran: ...


class Read(NamedTuple):
    """What overnight reads of a run: whether it's done, the session it ran in, where its result
    names one, and its result, or why it stopped."""

    done: bool
    session: str | None
    why: str


def command(tools: str, session: str | None) -> list[str]:
    """The words of a run of `claude` in non-interactive mode, giving its result as JSON.

    Takes: the tools that Claude may use, as `--allowed-tools` takes them, such as `Read,Edit`, and
    the session to go on in, or None for a new one.
    Gives: `claude -p --output-format json --allowed-tools <tools>`, with `--resume <session>`
    where a session is given. The prompt goes on stdin, as `--allowed-tools` takes each word after
    it as a tool.
    """
    words = ["claude", "-p", "--output-format", "json", "--allowed-tools", tools]
    return words if session is None else [*words, "--resume", session]


def run(argv: Sequence[str], cwd: str, stdin: str) -> Ran:
    """Runs `claude` as a process of its own, in the environment of overnight's own.

    Takes: the command's words, as `command` gives them, the folder to run it in, and its stdin.
    Gives: its exit code, stdout, and stderr, whatever the code, as `read` judges the result. A
    run killed by a signal gives the signal's number below 0, such as -9.
    Changes: whatever Claude does in the folder.
    """
    return subprocess.run(
        list(argv), cwd=cwd, input=stdin, capture_output=True, text=True, check=False
    )


def read(ran: Ran) -> Read:
    """Reads what a run of `claude -p --output-format json` gave.

    Gives: done only where the run exits 0 and its result says `is_error` false, as a run that
    the rate limit stops can exit 0 too (anthropics/claude-code#79500). The session is the result's
    `session_id`, or None where stdout holds no result. Why is the result's text, or else what the
    run wrote on stderr, or else `exit code <code>`.
    """
    try:
        result = json.loads(ran.stdout)
    except ValueError:
        result = {}
    done = ran.returncode == 0 and result.get("is_error") is False
    why = result.get("result") or ran.stderr.strip() or f"exit code {ran.returncode}"
    return Read(done, result.get("session_id"), why)
