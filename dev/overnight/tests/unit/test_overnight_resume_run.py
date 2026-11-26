"""The unit cases of resume as overnight's hook runs it, `python3 <scripts>/resume` with the
StopFailure hook's input on stdin, and of wait.py as the waiter runs it: the waiter that resumes the
session once the hook has ended, and wait.py, which sleeps its seconds and then becomes the command
it was given. Each runs the double of claude in place of the claude that the developer runs."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from typing import Any

import claude_double
import pytest
import resume
from resume.command import PROMPT

FOLDER = os.path.dirname(resume.__file__)
WAIT = os.path.join(FOLDER, "wait.py")


@pytest.fixture
def calls(tmp_path: Any) -> str:
    """The file where the double of claude keeps each call."""
    return os.path.join(str(tmp_path), "calls.jsonl")


def environment(path: str, calls: str) -> dict[str, str]:
    """The environment of the developer's run, such as coverage's settings, with PATH naming only
    the folder given, an interval of 1 second, and the double's file of calls."""
    return {
        **os.environ,
        "PATH": path,
        "OVERNIGHT_INTERVAL_SECONDS": "1",
        claude_double.CALLS: calls,
    }


def test_the_waiter_resumes_the_session_once_the_hook_has_ended(
    sessions: str, project: str, claude: str, calls: str
) -> None:
    """Given a session that ran in dontAsk and stopped at the usage limit, with claude on PATH and
    an interval of 1 second
    When the hook runs resume
    Then the hook gives 0 and says nothing, and after it has ended, claude resumes the session
    headless in dontAsk in the session's folder, told to go on"""
    transcript = claude_double.transcript(sessions, claude_double.prompt("dontAsk"))
    given = claude_double.stop_failure(transcript, project)

    ran = subprocess.run(
        [sys.executable, FOLDER],
        input=json.dumps(given).encode("utf-8"),
        capture_output=True,
        env=environment(os.path.dirname(claude), calls),
        check=False,
    )
    ended = time.time()

    assert (ran.returncode, ran.stdout, ran.stderr) == (0, b"", b"")
    [call] = claude_double.called(calls)
    assert call["argv"] == [
        "-p",
        "--resume",
        claude_double.session_id(),
        "--permission-mode",
        "dontAsk",
        PROMPT,
    ]
    assert call["cwd"] == project
    assert call["at"] > ended


def test_wait_becomes_the_command_once_its_seconds_are_over(claude: str, calls: str) -> None:
    """Given the double of claude
    When wait.py runs with 1 second and claude with its arguments
    Then after 1 second, the waiter's own process runs claude with those arguments, and exits as
    claude does"""
    started = time.time()

    waiter = subprocess.Popen(
        [sys.executable, WAIT, "1", claude, "-p", "--resume", "abc123", "go on"],
        env={**os.environ, claude_double.CALLS: calls},
    )
    code = waiter.wait()

    [call] = claude_double.called(calls)
    assert call["argv"] == ["-p", "--resume", "abc123", "go on"]
    assert call["pid"] == waiter.pid
    assert call["at"] - started >= 1
    assert code == claude_double.exit_code()
