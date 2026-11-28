"""The unit cases of the `overnight` command, as the user runs it from Claude Code's shell, which
has the plugin's bin/ on its PATH."""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import time
from typing import Callable

from double.claude_double import DONE, RATE_LIMIT, asked, put_on_path, session_of

# The top of the repository, four folders above this file's: unit/, tests/, overnight/, and dev/.
TOP = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
PLUGIN = os.path.join(TOP, "plugins", "overnight")
COMMAND = os.path.join(PLUGIN, "bin", "overnight")

# The python3 that runs the tests, which bin/overnight runs too.
PYTHON = os.path.dirname(sys.executable)
PROMPT = "Say ok"
# How long a case waits for the work that the command started apart to reach what it checks.
PATIENCE = 30


def _overnight(tmp_path, env: dict[str, str], *words: str) -> subprocess.CompletedProcess[str]:
    """Runs the command from the repository's top, as the checks run each test, with its home in
    the test's folder and the variables given."""
    return subprocess.run(
        [COMMAND, *words],
        cwd=TOP,
        env={**os.environ, **env, "HOME": str(tmp_path)},
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=False,
        timeout=PATIENCE,
    )


def _double(tmp_path, *events: str) -> tuple[dict[str, str], str]:
    """The variables that put the double of `claude` on the PATH, giving the events' runs, after
    the tests' python3, and the double's folder."""
    folder = tmp_path / "double"
    folder.mkdir()
    env = put_on_path(str(folder), *events)
    return {**env, "PATH": PYTHON + os.pathsep + env["PATH"]}, str(folder)


def _works(tmp_path) -> list[str]:
    """The folders of the works under the home's .local/state/overnight/, or [] where it's none."""
    top = tmp_path / ".local" / "state" / "overnight"
    return sorted(str(top / name) for name in os.listdir(top)) if top.exists() else []


def _until(check: Callable[[], bool]) -> None:
    deadline = time.monotonic() + PATIENCE
    while not check():
        assert time.monotonic() < deadline, "the work didn't get there in time"
        time.sleep(0.05)


def _gone(pid: int) -> bool:
    # A process whose parent has ended may stay as a zombie where nothing reaps it, which has
    # still ended, as `ps` shows by Z.
    shown = subprocess.run(
        ["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True, check=False
    )
    return shown.stdout.strip()[:1] in ("", "Z")


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _ended(folder: str, double: str) -> None:
    """Waits until the work in the folder has ended and its process with it."""
    state = os.path.join(folder, "state.json")
    _until(lambda: os.path.exists(state) and '"running"' not in _read(state))
    _until(lambda: _gone(asked(double)[0]["sid"]))


def _refused(tmp_path, env: dict[str, str], *words: str) -> tuple[int, str, str, list[str]]:
    """What the command gave for the words: its exit code, stdout, the last line of stderr, and
    the works it made."""
    ran = _overnight(tmp_path, env, *words)
    return ran.returncode, ran.stdout, ran.stderr.splitlines()[-1], _works(tmp_path)


def test_version_shows_the_version_that_plugin_json_holds(tmp_path):
    """Given the plugin, whose .claude-plugin/plugin.json holds its version
    When the user runs `overnight --version`, from the repository's top, as the checks run each test
    Then it exits 0, having written `overnight <that version>` on stdout and nothing on stderr"""
    with open(os.path.join(PLUGIN, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        version = json.load(f)["version"]
    ran = _overnight(tmp_path, {"PATH": PYTHON + os.pathsep + os.environ["PATH"]}, "--version")
    assert (ran.returncode, ran.stdout, ran.stderr) == (0, f"overnight {version}\n", "")


def test_a_work_starts_apart_from_the_session_and_ends_done(tmp_path):
    """Given a folder to work in, and `claude`, whose run is done
    When the user runs `overnight --dir <folder> --allowed-tools Read "Say ok"`
    Then it names the work and its state folder, and the work runs `claude -p` with the prompt in
    the folder, in a session apart from the user's, and is recorded done"""
    shop = tmp_path / "shop"
    shop.mkdir()
    env, double = _double(tmp_path, DONE)
    ran = _overnight(tmp_path, env, "--dir", str(shop), "--allowed-tools", "Read", PROMPT)
    [folder] = _works(tmp_path)
    work = os.path.basename(folder)
    assert (ran.returncode, ran.stdout, ran.stderr) == (
        0,
        f"overnight: work {work} started in {shop}\novernight: state and log in {folder}/\n",
        "",
    )
    assert re.fullmatch(r"\d{8}-\d{6}", work)
    _ended(folder, double)
    [call] = asked(double)
    assert call["sid"] != os.getsid(0)
    assert (call["argv"], call["cwd"], call["stdin"]) == (
        ["claude", "-p", "--output-format", "json", "--allowed-tools", "Read"],
        str(shop),
        PROMPT,
    )
    assert json.loads(_read(os.path.join(folder, "state.json"))) == {
        "status": "done",
        "dir": str(shop),
        "session_id": session_of(DONE),
        "runs": 1,
    }
    assert re.fullmatch(
        rf"\d\d:\d\d run 1 started\n\d\d:\d\d run 1 done\nwork {work} done after 1 run\n",
        _read(os.path.join(folder, "log")),
    )


def _first_retry(tmp_path, *words: str) -> str:
    """The log of a work that the words start, where `claude`'s run the rate limit stops, once it
    names its first retry, with the work then stopped."""
    env, double = _double(tmp_path, RATE_LIMIT)
    _overnight(tmp_path, env, "--dir", str(tmp_path), "--allowed-tools", "Read", *words)
    [folder] = _works(tmp_path)
    log = os.path.join(folder, "log")
    _until(lambda: os.path.exists(log) and "Retry" in _read(log))
    os.killpg(asked(double)[0]["sid"], signal.SIGTERM)
    return _read(log)


def test_a_stopped_run_is_retried_7_times_where_retries_isnt_given(tmp_path):
    """Given `claude`, whose run the rate limit stops
    When the user starts a work with no `--retries`
    Then the work's log says that the run stopped, and names its first retry of 7"""
    log = _first_retry(tmp_path, PROMPT)
    assert re.fullmatch(
        r"\d\d:\d\d run 1 started\n\d\d:\d\d run 1 stopped: API Error: Rate limit reached\. "
        r"Retry 1 of 7 at \d\d:\d\d\.\n",
        log,
    ), log


def test_a_stopped_run_is_retried_as_many_times_as_retries_says(tmp_path):
    """Given `claude`, whose run the rate limit stops
    When the user starts a work with `--retries 10`
    Then the work's log says that the run stopped, and names its first retry of 10"""
    log = _first_retry(tmp_path, "--retries", "10", PROMPT)
    assert re.fullmatch(
        r"\d\d:\d\d run 1 started\n\d\d:\d\d run 1 stopped: API Error: Rate limit reached\. "
        r"Retry 1 of 10 at \d\d:\d\d\.\n",
        log,
    ), log


def test_a_work_with_0_retries_fails_at_its_first_stop(tmp_path):
    """Given `claude`, whose run the rate limit stops
    When the user starts a work with `--retries 0`, the fewest it takes
    Then the work starts, and its log says that the run stopped with no retries left, and that the
    work failed after 1 run"""
    env, double = _double(tmp_path, RATE_LIMIT)
    words = ["--dir", str(tmp_path), "--retries", "0", "--allowed-tools", "Read", PROMPT]
    ran = _overnight(tmp_path, env, *words)
    [folder] = _works(tmp_path)
    assert (ran.returncode, ran.stderr) == (0, "")
    _ended(folder, double)
    assert re.fullmatch(
        r"\d\d:\d\d run 1 started\n\d\d:\d\d run 1 stopped: API Error: Rate limit reached\. "
        rf"No retries left\.\nwork {os.path.basename(folder)} failed after 1 run\n",
        _read(os.path.join(folder, "log")),
    )


def test_a_dir_that_isnt_a_folder_is_refused(tmp_path):
    """Given no folder at the path the user names
    When the user runs `overnight --dir <that path> ...`
    Then it exits 2, saying the path names no folder, and starts no work"""
    env, _ = _double(tmp_path, DONE)
    missing = str(tmp_path / "shop")
    assert _refused(tmp_path, env, "--dir", missing, "--allowed-tools", "Read", PROMPT) == (
        2,
        "",
        f"overnight: error: --dir {missing}: no such folder",
        [],
    )


def test_retries_that_arent_a_whole_number_are_refused(tmp_path):
    """Given the user's count of retries, `two`
    When the user runs `overnight --retries two ...`
    Then it exits 2, saying the count must be a whole number from 0, and starts no work"""
    env, _ = _double(tmp_path, DONE)
    words = ["--dir", str(tmp_path), "--retries", "two", "--allowed-tools", "Read", PROMPT]
    assert _refused(tmp_path, env, *words) == (
        2,
        "",
        "overnight: error: argument --retries: must be a whole number from 0, not 'two'",
        [],
    )


def test_retries_below_0_are_refused(tmp_path):
    """Given the user's count of retries, -1, just below the fewest
    When the user runs `overnight --retries -1 ...`
    Then it exits 2, saying the count must be a whole number from 0, and starts no work"""
    env, _ = _double(tmp_path, DONE)
    words = ["--dir", str(tmp_path), "--retries=-1", "--allowed-tools", "Read", PROMPT]
    assert _refused(tmp_path, env, *words) == (
        2,
        "",
        "overnight: error: argument --retries: must be a whole number from 0, not '-1'",
        [],
    )


def test_an_empty_prompt_is_refused(tmp_path):
    """Given a prompt of only spaces
    When the user runs `overnight ... " "`
    Then it exits 2, saying the prompt is empty, and starts no work"""
    env, _ = _double(tmp_path, DONE)
    assert _refused(tmp_path, env, "--dir", str(tmp_path), "--allowed-tools", "Read", " ") == (
        2,
        "",
        "overnight: error: the prompt is empty: give the work's prompt as the last word, in quotes",
        [],
    )


def test_a_work_with_no_tools_named_is_refused(tmp_path):
    """Given a work with no `--allowed-tools`
    When the user runs `overnight --dir <folder> "Say ok"`
    Then it exits 2, saying `--allowed-tools` is required, and starts no work"""
    env, _ = _double(tmp_path, DONE)
    assert _refused(tmp_path, env, "--dir", str(tmp_path), PROMPT) == (
        2,
        "",
        "overnight: error: the following arguments are required: --allowed-tools",
        [],
    )


def test_a_work_with_no_claude_on_the_path_is_refused(tmp_path):
    """Given a PATH with no `claude` on it
    When the user runs `overnight ...`
    Then it exits 2, saying where to run it from, and starts no work"""
    env = {"PATH": os.pathsep.join([PYTHON, "/usr/bin", "/bin"])}
    assert _refused(tmp_path, env, "--dir", str(tmp_path), "--allowed-tools", "Read", PROMPT) == (
        2,
        "",
        (
            "overnight: error: claude isn't on the PATH: run overnight from Claude Code, as"
            " `! overnight ...`"
        ),
        [],
    )
