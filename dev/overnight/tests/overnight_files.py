"""What overnight's cases make and read around its code: the person's repository, git run in it, the
environment of each command, a process that runs and one that ended, and the walkthrough's words,
its piece's folder and branch among them."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from collections.abc import Callable, Iterable

from pieces.record import Handed

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
PLUGIN = os.path.join(TOP, "plugins", "overnight")

# The walkthrough's repository, and the prompt and tools of its piece for #12, as the README gives
# them.
REPOSITORY = "myapp"
PROMPT = (
    'Fix issue #12: parse_date raises on "2026-02-29 00:00". Make'
    " tests/test_dates.py::test_leap_day pass, and change no other test. Run pytest to check, then"
    " commit on this branch.\n"
)
TOOLS = ("Read", "Edit", "Bash(pytest:*)", "Bash(git add:*)", "Bash(git commit:*)")
# The tools as ask hands them on, from the prompt's last line, `Tools: <tool>, <tool>`.
TOOLS_LINE = ", ".join(TOOLS)
# A prompt of several lines that starts with an option of Claude Code's, and holds quotes, a line
# `Tools:`, words beyond ASCII, and a blank line, which reaches Claude Code whole only on its
# standard input.
PROMPT_AS_OPTIONS = (
    "--resume 1234 \"quoted\" and 'single'\nTools: Bash\n日付の解析を直す。\n\nThen commit.\n"
)
# The last words of each of the walkthrough's three pieces.
LAST_WORDS = (
    "Fixed parse_date for leap days. 214 tests pass.",
    "Kept the CSV header in its column order. 214 tests pass.",
    "Added the --dry-run flag. 216 tests pass.",
)
# The share line of a night, as the README's walkthrough shows it.
SHARE = "{} of {} pieces stopped by the usage limit, a wait for an answer, or the session closing."
# The table that status shows of the walkthrough's night, as the README gives it.
WALKTHROUGH_TABLE = (
    "Piece  State  Branch       Waited                       Last words\n"
    f"1      done   overnight/1  -                            {LAST_WORDS[0]}\n"
    f"2      done   overnight/2  usage limit, 01:12 to 04:00  {LAST_WORDS[1]}\n"
    f"3      done   overnight/3  usage limit, 01:12 to 04:00  {LAST_WORDS[2]}\n"
    "\n"
    f"{SHARE.format(0, 3)}\n"
)

# Who commits in each repository that a case makes, as git asks for a name and an email.
IDENTITY = {
    "GIT_AUTHOR_NAME": "Person",
    "GIT_AUTHOR_EMAIL": "person@example.com",
    "GIT_COMMITTER_NAME": "Person",
    "GIT_COMMITTER_EMAIL": "person@example.com",
}
# The settings by which coverage counts a process that a case starts.
COVERAGE_SETTINGS = ("COVERAGE_PROCESS_START", "COVERAGE_FILE")


def git(repo: str, *args: str) -> str:
    """Runs git in the repository, and gives what it printed."""
    env = {**os.environ, **IDENTITY}
    done = subprocess.run(
        ["git", "-C", repo, *args], capture_output=True, text=True, check=True, env=env
    )
    return done.stdout


def repository(folder: str, name: str = REPOSITORY, commit: bool = True) -> str:
    """Makes the person's repository `<folder>/<name>`, a Python app on the branch main, with its
    first commit where `commit` is true, and `.overnight/` in its `.gitignore`, and gives its
    path."""
    repo = os.path.join(folder, name)
    os.makedirs(os.path.join(repo, "tests"))
    git(repo, "init", "-q", "-b", "main")
    files = {
        "app.py": "def parse_date(text):\n    return text\n",
        "tests/test_dates.py": "def test_leap_day():\n    pass\n",
        ".gitignore": ".overnight/\n",
    }
    for path, text in files.items():
        with open(os.path.join(repo, path), "w", encoding="utf-8") as f:
            f.write(text)
    if commit:
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "The app")
    return repo


def environment(tmp: str, first: Iterable[str] = ()) -> dict[str, str]:
    """The environment of each command a case in the folder runs: each folder of `first` ahead of
    the PATH, a home and a system's temporary folder of its own, the latter made, git's identity,
    and, where check.sh measures coverage, its settings."""
    path = os.pathsep.join([*first, os.environ.get("PATH", os.defpath)])
    env = {
        "PATH": path,
        "HOME": os.path.join(tmp, "home"),
        "TMPDIR": os.path.join(tmp, "system-temp"),
        **IDENTITY,
    }
    env.update({name: os.environ[name] for name in COVERAGE_SETTINGS if name in os.environ})
    if "SYSTEMROOT" in os.environ:
        env["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
    os.makedirs(env["TMPDIR"], exist_ok=True)
    return env


def alive(pid: int) -> bool:
    """Whether a process with the ID runs, as its OS tells."""
    if os.name == "nt":
        listed = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True, check=False
        )
        return str(pid) in listed.stdout
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def kill(pid: int) -> None:
    """Ends the process with the ID at once, as an OS that shuts it down would, where it runs."""
    try:
        os.kill(pid, getattr(signal, "SIGKILL", signal.SIGTERM))
    except (ProcessLookupError, PermissionError, OSError):
        pass


def until(check: Callable[[], bool], timeout: float = 30.0, what: str = "the condition") -> None:
    """Waits until the check gives true, or fails the case naming what it waited for."""
    end = time.monotonic() + timeout
    while not check():
        if time.monotonic() > end:
            raise AssertionError(f"waited {timeout:.0f}s for {what}")
        time.sleep(0.05)


def running_process() -> subprocess.Popen:
    """A child process that runs until the case ends it, as a runner that carries a piece."""
    return subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])


def shut_down(child: subprocess.Popen) -> None:
    """Ends the child process at once, as the OS shuts a runner down, and waits until it has, so
    that no process with its ID is left."""
    child.kill()
    child.wait()


def ended_process() -> int:
    """The ID of a process that ran and has ended."""
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    child.wait()
    return child.pid


def piece_folder(repo: str, number: int) -> str:
    """Where the piece of the number works: `../<repository>-overnight-<n>/` beside the
    repository."""
    return os.path.join(os.path.dirname(repo), f"{os.path.basename(repo)}-overnight-{number}")


def handed(number: int = 1, tools: tuple[str, ...] = TOOLS) -> Handed:
    """The walkthrough's piece of the number with the tools, as hand-over hands it on: in
    `../myapp-overnight-<n>` on the branch `overnight/<n>`."""
    return Handed(number, f"../{REPOSITORY}-overnight-{number}", f"overnight/{number}", tools)


def handover_lines(number: int, tools: str = TOOLS_LINE) -> str:
    """The lines that handover.py gives for the walkthrough's piece of the number, as the README's
    walkthrough shows them."""
    piece = handed(number)
    return (
        f"Piece {number} runs in the background, apart from this session.\n"
        f"Folder: {piece.folder}, on the branch {piece.branch}\n"
        f"Tools: {tools}\n"
        "/overnight:status shows how it goes.\n"
    )
