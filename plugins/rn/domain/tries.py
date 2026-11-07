"""Where a deliverable's commands run, and what of them the try record keeps: a throwaway copy of
the repository and a throwaway home, in the run's folder in the system's temporary folder, each file
the Making record names under the home made there empty, each command run there in its order by the
shell, with the home as the environment's own so `~` names it, and each command with what it printed
and its exit code written into the round's `throwaway.txt`; the copy and the home removed whatever
the commands do. A command run as the people run it, such as `tidy` on a Downloads folder, then
changes none of the user's own files."""

from __future__ import annotations

import os
import shutil
import subprocess

import runs
import starts
import trees
from starts import Stop

# The seconds a command may run before the try stops it, as a command that waits for input would
# hold the round for ever.
SECONDS = 300


def under_home(path: str) -> bool:
    """Whether the path names a file under the home: relative, and not the home itself nor out of
    it by `..`."""
    named = os.path.normpath(path)
    return not os.path.isabs(path) and named not in (".", "..") and not named.startswith("../")


def round_at(run: str) -> str:
    """The round of the turn at hand of the run; refuses, by Stop, a run with none."""
    tree = starts.the_tree(run)
    n = trees.at_hand(tree)
    d = trees.deliverables(tree)[n - 1] if n is not None else None
    rounds = runs.rounds(runs.turn_of(run, d["path"], starts.reads(d))) if d else []
    if not rounds or runs.made_of(rounds[-1]) is None:
        raise Stop(f"{run} has no round with a Making record to try: write it first")
    return rounds[-1]


def run_each(commands: list[str], copy: str, home: str) -> str:
    """Each command run in the copy with the home, and what it gave, as the try record holds it."""
    env = {**os.environ, "HOME": home}
    out = []
    for command in commands:
        try:
            done = subprocess.run(
                command,
                shell=True,
                cwd=copy,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=SECONDS,
                check=False,
            )
            out.append(f"$ {command}\n{done.stdout}(exit {done.returncode})\n")
        except subprocess.TimeoutExpired as late:
            # What the command printed before the stop comes as bytes, whatever the call asked for.
            given = late.stdout or b""
            said = given.decode(errors="replace") if isinstance(given, bytes) else given
            out.append(f"$ {command}\n{said}(stopped after {SECONDS} seconds)\n")
    return "".join(out)


def tried(run: str) -> str:
    """Runs the commands of the round at hand's Making record in a throwaway copy, and writes what
    each gave into the round's try record: the path written."""
    round_ = round_at(run)
    record = runs.made_of(round_) or {}
    home_files = record.get("home", [])
    out = [f for f in home_files if not under_home(f)]
    if out:
        raise Stop(f"the file {out[0]} lies out of the home")
    path = os.path.join(round_, runs.TRY)
    commands = record.get("commands", [])
    if not commands:
        with open(path, "w", encoding="utf-8") as f:
            f.write("No command tries the deliverable.\n")
        return path
    top = os.path.join(runs.temporary(run), "try")
    shutil.rmtree(top, ignore_errors=True)
    try:
        copy, home = os.path.join(top, "copy"), os.path.join(top, "home")
        # The copy takes a link as the file it reaches, so a write in the copy reaches nothing
        # outside it.
        shutil.copytree(".", copy, ignore_dangling_symlinks=True)
        os.makedirs(home)
        for name in home_files:
            made = os.path.join(home, name)
            os.makedirs(os.path.dirname(made), exist_ok=True)
            with open(made, "w", encoding="utf-8"):
                pass
        said = run_each(commands, copy, home)
    finally:
        shutil.rmtree(top, ignore_errors=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(said)
    return path
