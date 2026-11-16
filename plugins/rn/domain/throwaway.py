"""Decides how a deliverable's command runs where it can't change the user's files: in a throwaway
copy of rn's worktree, with a throwaway home, each command tried kept in the round's Try record."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from collections.abc import Sequence
from dataclasses import asdict, dataclass

from fault import Missing, Wrong
from tree import rounds, runs

USAGE = "usage: throwaway.py <deliverable> <command, as one argument>\n"


@dataclass(frozen=True)
class Tried:
    """One command tried: the command, its exit code, and what it printed to stdout and stderr."""

    command: str
    code: int
    out: str
    err: str


def main(argv: Sequence[str], cwd: str) -> tuple[int, str, str]:
    """Runs throwaway.py.

    Takes: the command line after `throwaway.py`, `<deliverable> <command>`, and the folder it runs
    in, which lies in a run's worktree.
    Gives, as the exit code, standard output, and standard error: the command's own, run by `sh -c`
    in a copy of the worktree with HOME set to a throwaway folder, both in the system's temporary
    folder and removed once it ends; 1, with what's wrong, where the folder lies in no run's
    worktree or the deliverable has no round; 2, with the usage.
    Changes: adds the Tried to the file that `tree.rounds.try_path` names.
    Refuses: as Gives says, by its exit code.
    Carries: S1 `G->>W: tries it (Try record)`.
    """
    if len(argv) != 2:
        return 2, "", USAGE
    deliverable, command = argv
    try:
        run = runs.of_folder(cwd)
        if run is None:
            raise Wrong(f"{cwd} lies in no run's worktree, whose copy a command runs in")
        kept = os.path.join(run.worktree, rounds.try_path(run, deliverable))
    except (Wrong, Missing) as e:
        return 1, "", f"throwaway.py: {e}\n"
    within = os.path.relpath(os.path.realpath(cwd), run.worktree)
    tried = _tried(
        run.worktree, os.path.join(tempfile.gettempdir(), "rn", run.name), within, command
    )
    _keep(kept, tried)
    return tried.code, tried.out, tried.err


def _tried(worktree: str, temporary: str, within: str, command: str) -> Tried:
    """The command run in a copy of the worktree, at the same folder within it, with a home of its
    own, both in a folder of the run's in the system's temporary folder and removed once it ends.
    The copy leaves out the worktree's link to its repository, `.git`, so that no git command it
    runs reaches the work's branch."""
    os.makedirs(temporary, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="throwaway-", dir=temporary) as folder:
        copy = os.path.join(folder, "worktree")
        shutil.copytree(worktree, copy, symlinks=True, ignore=shutil.ignore_patterns(".git"))
        home = os.path.join(folder, "home")
        os.makedirs(home)
        done = subprocess.run(
            ["sh", "-c", command],
            cwd=os.path.normpath(os.path.join(copy, within)),
            env=dict(os.environ, HOME=home),
            capture_output=True,
            text=True,
            check=False,
        )
    return Tried(command, done.returncode, done.stdout, done.stderr)


def _keep(path: str, tried: Tried) -> None:
    """Adds the Tried to the round's Try record as a JSON line of its own, after each one tried
    before, so that a try adds to the record without reading it."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(tried)) + "\n")
