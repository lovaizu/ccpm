"""The cases of the `overnight` command, as its user types it in Claude Code's bash mode."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import time
from typing import Any

from claude import claude_double
from conftest import PLUGIN

OVERNIGHT = os.path.join(PLUGIN, "bin", "overnight")
TOOLS = "Read,Edit,Bash(pytest:*)"
PROMPT = "Move the tests in tests/unittest_old/ to pytest"
# How long a case waits for the work that it started to end, far past the moment that a work of
# one run of the double takes.
_END = 30


def test_version_names_the_plugin_and_its_version() -> None:
    """Given overnight 0.1.0, installed
    When the user runs `overnight --version`
    Then it prints `overnight 0.1.0` and exits 0."""
    ran = subprocess.run([OVERNIGHT, "--version"], capture_output=True, text=True, check=False)

    assert (ran.returncode, ran.stdout, ran.stderr) == (0, "overnight 0.1.0\n", "")


def test_help_says_the_prompt_is_required() -> None:
    """Given overnight, installed
    When the user runs `overnight --help`
    Then it lists the prompt as required."""
    assert "prompt what the work is, as you would ask Claude (required)" in help_text()


def test_help_says_dir_defaults_to_the_folder_overnight_is_started_in() -> None:
    """Given overnight, installed
    When the user runs `overnight --help`
    Then it lists `--dir`, whose default is the folder that overnight is started in."""
    assert (
        "--dir DIR the folder the work runs in (default: the folder overnight is started in)"
        in help_text()
    )


def test_help_says_allowed_tools_is_required() -> None:
    """Given overnight, installed
    When the user runs `overnight --help`
    Then it lists `--allowed-tools` as required."""
    assert (
        "--allowed-tools TOOLS the tools that Claude may use for the work, as `claude"
        ' --allowed-tools` takes them, such as "Read,Edit,Bash(pytest:*)" (required)' in help_text()
    )


def test_help_says_retries_defaults_to_7() -> None:
    """Given overnight, installed
    When the user runs `overnight --help`
    Then it lists `--retries`, whose default is 7."""
    assert "--retries COUNT how many times a stopped work is retried (default: 7)" in help_text()


def test_start_prints_the_work_and_the_folder_of_its_state_and_log(
    double: claude_double.Double, work_dir: str, home: str
) -> None:
    """Given a work to run in a folder
    When the user starts it by `overnight --dir`
    Then overnight prints the work's ID and folder, and the folder of its state and log, and exits
    0."""
    double.answer(claude_double.DONE)

    ran = overnight("--dir", work_dir, "--allowed-tools", TOOLS, PROMPT)

    work = the_work(home)
    assert (ran.returncode, ran.stdout, ran.stderr) == (
        0,
        (
            f"overnight: work {os.path.basename(work)} started in {work_dir}\n"
            f"overnight: state and log in {work}/\n"
        ),
        "",
    )


def test_a_started_work_is_carried_through_after_overnight_returns(
    double: claude_double.Double, work_dir: str, home: str
) -> None:
    """Given a work whose first run ends with no error
    When the user starts it by overnight
    Then, after overnight returns, the work runs its prompt with its tools in its folder, and is
    recorded as done after 1 run."""
    double.answer(claude_double.DONE)

    overnight("--dir", work_dir, "--allowed-tools", TOOLS, PROMPT)

    state = ended(the_work(home))
    call = double.calls()[0]
    assert (state, call["args"], call["stdin"], call["cwd"]) == (
        {"status": "done", "dir": work_dir, "session_id": claude_double.SESSION_ID, "runs": 1},
        ["-p", "--output-format", "json", "--allowed-tools", TOOLS],
        PROMPT,
        work_dir,
    )


def test_a_started_work_runs_in_a_session_apart_from_the_one_that_starts_it(
    double: claude_double.Double, work_dir: str, home: str
) -> None:
    """Given a work to run
    When the user starts it by overnight
    Then Claude Code runs in a session of processes apart from the one that started overnight, so
    that closing Claude Code doesn't stop it."""
    double.answer(claude_double.DONE)

    overnight("--dir", work_dir, "--allowed-tools", TOOLS, PROMPT)

    ended(the_work(home))
    assert double.calls()[0]["sid"] != os.getsid(0)


def test_a_started_work_writes_its_errors_to_its_log(
    double: claude_double.Double, work_dir: str, home: str
) -> None:
    """Given a started work that waits for its retry after the usage limit
    When the work is interrupted
    Then its log ends with the error that stopped it."""
    double.answer(claude_double.LIMIT)
    overnight("--dir", work_dir, "--allowed-tools", TOOLS, PROMPT)
    work = the_work(home)
    logged(work, "Retry 1 of 7")

    os.kill(double.calls()[0]["sid"], signal.SIGINT)

    assert logged(work, "KeyboardInterrupt").splitlines()[-1] == "KeyboardInterrupt"


def test_dir_defaults_to_the_folder_overnight_is_started_in(
    double: claude_double.Double, work_dir: str, home: str
) -> None:
    """Given a work started with no `--dir`
    When overnight runs it
    Then the work runs in the folder that overnight was started in."""
    double.answer(claude_double.DONE)

    overnight("--allowed-tools", TOOLS, PROMPT, cwd=work_dir)

    assert (ended(the_work(home))["dir"], double.calls()[0]["cwd"]) == (work_dir, work_dir)


def test_retries_sets_how_many_times_a_stopped_work_is_retried(
    double: claude_double.Double, work_dir: str, home: str
) -> None:
    """Given a work whose first run the usage limit stops
    When the user starts it with `--retries 0`
    Then the work is recorded as failed after 1 run, with no retry."""
    double.answer(claude_double.LIMIT)

    overnight("--dir", work_dir, "--allowed-tools", TOOLS, "--retries", "0", PROMPT)

    assert ended(the_work(home)) == {
        "status": "failed",
        "dir": work_dir,
        "session_id": claude_double.SESSION_ID,
        "runs": 1,
    }


def test_refuses_a_work_with_no_allowed_tools(work_dir: str, home: str) -> None:
    """Given a work started with no `--allowed-tools`
    When overnight reads its arguments
    Then it says `--allowed-tools` is required, exits 2, and starts no work."""
    ran = overnight("--dir", work_dir, PROMPT)

    assert refusal(ran, home) == (2, "the following arguments are required: --allowed-tools")


def test_refuses_empty_allowed_tools(work_dir: str, home: str) -> None:
    """Given a work started with `--allowed-tools ""`
    When overnight reads its arguments
    Then it says `--allowed-tools` is empty, exits 2, and starts no work."""
    ran = overnight("--dir", work_dir, "--allowed-tools", "", PROMPT)

    assert refusal(ran, home) == (
        2,
        "--allowed-tools is empty: name the tools that Claude may use for the work",
    )


def test_refuses_a_dir_that_isnt_a_folder(work_dir: str, home: str) -> None:
    """Given a work started with `--dir` naming no folder
    When overnight reads its arguments
    Then it names the `--dir` it was given, exits 2, and starts no work."""
    missing = os.path.join(work_dir, "gone")

    ran = overnight("--dir", missing, "--allowed-tools", TOOLS, PROMPT)

    assert refusal(ran, home) == (2, f"--dir {missing}: no such folder")


def test_refuses_retries_that_arent_a_whole_number(work_dir: str, home: str) -> None:
    """Given a work started with `--retries seven`
    When overnight reads its arguments
    Then it says what `--retries` takes, exits 2, and starts no work."""
    ran = overnight("--dir", work_dir, "--allowed-tools", TOOLS, "--retries", "seven", PROMPT)

    assert refusal(ran, home) == (
        2,
        'argument --retries: must be a whole number from 0, not "seven"',
    )


def test_refuses_retries_below_0(work_dir: str, home: str) -> None:
    """Given a work started with `--retries -1`
    When overnight reads its arguments
    Then it says what `--retries` takes, exits 2, and starts no work."""
    ran = overnight("--dir", work_dir, "--allowed-tools", TOOLS, "--retries=-1", PROMPT)

    assert refusal(ran, home) == (2, 'argument --retries: must be a whole number from 0, not "-1"')


def test_refuses_an_empty_prompt(work_dir: str, home: str) -> None:
    """Given a work started with an empty prompt
    When overnight reads its arguments
    Then it says the prompt is empty, exits 2, and starts no work."""
    ran = overnight("--dir", work_dir, "--allowed-tools", TOOLS, "")

    assert refusal(ran, home) == (2, "the prompt is empty: say what the work is")


def test_refuses_to_start_where_no_claude_is_on_the_path(
    work_dir: str, home: str, monkeypatch: Any
) -> None:
    """Given a PATH that holds no claude
    When the user starts a work by overnight
    Then it says no claude is on the PATH, exits 2, and starts no work."""
    monkeypatch.setenv("PATH", without_claude(os.environ["PATH"]))

    ran = overnight("--dir", work_dir, "--allowed-tools", TOOLS, PROMPT)

    assert refusal(ran, home) == (
        2,
        "no claude is on the PATH: install Claude Code, or add its folder to the PATH",
    )


def overnight(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run([OVERNIGHT, *args], capture_output=True, text=True, cwd=cwd, check=False)


def help_text() -> str:
    """What `overnight --help` prints, its spaces and line breaks each as one space, as the width
    of the terminal decides where it breaks."""
    ran = overnight("--help")
    assert ran.returncode == 0
    return " ".join(ran.stdout.split())


def the_work(home: str) -> str:
    """The folder of the one work that the case started."""
    states = os.path.join(home, ".local", "state", "overnight")
    (work,) = os.listdir(states)
    return os.path.join(states, work)


def ended(work: str) -> dict[str, Any]:
    """The state of `work` once it's no longer running."""
    deadline = time.monotonic() + _END
    while time.monotonic() < deadline:
        with open(os.path.join(work, "state.json"), encoding="utf-8") as f:
            state = json.load(f)
        if state["status"] != "running":
            return state
        time.sleep(0.05)
    raise AssertionError(f"{work} still runs after {_END} seconds")


def logged(work: str, text: str) -> str:
    """The log of `work` once it holds `text`."""
    deadline = time.monotonic() + _END
    while time.monotonic() < deadline:
        with open(os.path.join(work, "log"), encoding="utf-8") as f:
            log = f.read()
        if text in log:
            return log
        time.sleep(0.05)
    raise AssertionError(f"the log of {work} still lacks {text!r} after {_END} seconds")


def refusal(ran: subprocess.CompletedProcess[str], home: str) -> tuple[int, str]:
    """The exit code of a refused start and its message, after `overnight: error: `, once the case
    has checked that the refusal printed nothing on stdout and started no work."""
    assert (ran.stdout, os.path.exists(os.path.join(home, ".local", "state"))) == ("", False)
    return ran.returncode, ran.stderr.splitlines()[-1].removeprefix("overnight: error: ")


def without_claude(path: str) -> str:
    """`path` with each folder that holds a claude left out."""
    folders = path.split(os.pathsep)
    return os.pathsep.join(f for f in folders if not os.path.exists(os.path.join(f, "claude")))
