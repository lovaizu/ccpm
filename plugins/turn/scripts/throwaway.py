"""What the generator and the evaluator run the work's commands by, as `python3
${CLAUDE_PLUGIN_ROOT}/scripts/throwaway.py <run>`, so a command its user runs never reaches the
person's own files: it makes a throwaway home and a throwaway copy of the folder it is run in,
makes each file the work names, empty, at its path under the home, runs each command of the work
the run is at in order in the copy by the shell, the home as HOME so that `~` names it, prints each
command, what it printed and its exit code as the command ends, and removes both with shutil
whatever the commands do, giving 0; or, where it cannot read the run or a file lies out of the home,
prints why and gives 2, running nothing."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

# No module before it on the path has the name of Turn's.
sys.path.insert(
    0,  # pragma: no mutate
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", "domain"),
)

import files
import runs

USAGE = "usage: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/throwaway.py <run>"


def main(argv: list[str]) -> int:
    """Runs the commands of the run given as the module says, giving 0; or prints why it cannot,
    or the usage, and gives 2."""
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    [run] = argv
    try:
        work = runs.current(runs.load(run))
        out = [f for f in work["files"] if not under_home(f)]
        if out:
            raise files.Unreadable(f"the file {out[0]} lies out of the home")
    except files.Unreadable as why:
        print(f"throwaway.py: could not run the work's commands: {why}", file=sys.stderr)
        return 2
    if not work["commands"]:
        print("throwaway.py: the work has no commands.")
        return 0
    top = tempfile.mkdtemp(prefix="turn-throwaway-")
    try:
        home, copy = os.path.join(top, "home"), os.path.join(top, "work")
        # A link is copied as the file it reaches, so a write in the copy reaches nothing outside.
        shutil.copytree(os.getcwd(), copy, ignore_dangling_symlinks=True)
        for name in work["files"]:
            path = os.path.join(home, name)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8"):
                pass
        os.makedirs(home, exist_ok=True)
        env = {**os.environ, "HOME": home}
        for command in work["commands"]:
            done = subprocess.run(
                command,
                shell=True,
                cwd=copy,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
            print(f"$ {command}\n{done.stdout}(exit {done.returncode})", flush=True)
        return 0
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
