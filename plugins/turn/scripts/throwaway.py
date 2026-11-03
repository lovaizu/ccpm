"""What builder and evaluator run each of a work's commands by, as `python3
${CLAUDE_PLUGIN_ROOT}/scripts/throwaway.py [--file <path under ~>]... -- <command>`, so a command
used as the work's user uses it never reaches the person's own files and needs no shell set-up of
its own: it makes a throwaway home and a throwaway copy of the folder it is run in, makes each file
given, empty, at its path under the home, runs the command in the copy by the shell, the home as
HOME so that `~` names it, and removes both with shutil whatever the command does, giving the
command's exit code; or, where it is not called as it takes, prints its usage and gives 2."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

USAGE = (
    "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/throwaway.py [--file <path under ~>]..."
    " -- <command>"
)


def main(argv: list[str]) -> int:
    """Runs the command given after `--` as the module says, giving its exit code; or prints the
    usage and gives 2, running nothing, where no one command follows `--` or a file given does not
    lie under the home."""
    files: list[str] = []
    rest = list(argv)
    while rest[:1] == ["--file"] and len(rest) > 1 and rest[1] != "--":
        files.append(rest[1])
        rest = rest[2:]
    if rest[:1] != ["--"] or len(rest) != 2 or not all(map(under_home, files)):
        print(USAGE, file=sys.stderr)
        return 2
    top = tempfile.mkdtemp(prefix="turn-throwaway-")
    try:
        home, work = os.path.join(top, "home"), os.path.join(top, "work")
        shutil.copytree(os.getcwd(), work, symlinks=True)
        for name in files:
            path = os.path.join(home, name)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8"):
                pass
        os.makedirs(home, exist_ok=True)
        env = {**os.environ, "HOME": home}
        return subprocess.run(rest[1], shell=True, cwd=work, env=env, check=False).returncode
    finally:
        shutil.rmtree(top)


def under_home(path: str) -> bool:
    """Whether the path names a file under the home: relative, and not the home itself nor out of
    it by `..`."""
    named = os.path.normpath(path)
    return not os.path.isabs(path) and named not in (".", "..") and not named.startswith("../")


# Run as the command, and not when the tests import it under the name throwaway.
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.argv[1:]))
