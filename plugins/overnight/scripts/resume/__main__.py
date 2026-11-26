"""resume, as Claude Code runs it when a turn ends at the usage limit, by overnight's
`hooks/hooks.json`: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/resume"`, with the StopFailure hook's
input on stdin. It runs the code of this folder, whose `command` module says what it takes and
gives."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

# Python puts this folder first on the import path. The code imports its package from scripts/,
# this folder's parent, so that folder takes its place.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[0] = os.path.dirname(HERE)

from resume.command import main


def _leave(argv: list[str], cwd: str) -> None:
    """Starts the waiter in a session of its own, so that it outlives the hook and the Claude Code
    process that ran it, with its output closed, as Claude Code otherwise waits on it."""
    subprocess.Popen(
        argv,
        cwd=cwd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


if __name__ == "__main__":
    code, said = main(
        sys.stdin.buffer.read(),
        os.environ,
        shutil.which("claude"),
        [sys.executable, os.path.join(HERE, "wait.py")],
        _leave,
    )
    sys.stderr.write(said)
    raise SystemExit(code)
