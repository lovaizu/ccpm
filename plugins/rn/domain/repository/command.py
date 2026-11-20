"""Decides repository.py's command line: its subcommands, what each takes and prints, and the exit
code by which whoever ran it reads its result."""

from __future__ import annotations

import os
from collections.abc import Sequence
from datetime import date
from typing import Callable

import practice
from fault import CantRun, Missing, Wrong
from rounds import files

from repository import commit_checks, place, push, trial, worktree
from repository.host import Host

# Each subcommand's least and most count of arguments after its name, None where it takes any more.
_ARITY: dict[str, tuple[int, int | None]] = {
    "new": (2, 2),
    "find": (0, 0),
    "pause": (1, 1),
    "put-up": (2, 2),
    "checks": (1, None),
    "trial": (2, 2),
}

USAGE = """\
usage: repository.py new <words> <goal>
       repository.py find
       repository.py pause <run>
       repository.py put-up <run> <deliverable>
       repository.py checks <run> <file>...
       repository.py trial <run> <round>
"""


def main(argv: Sequence[str], cwd: str, plugin_root: str, host: Host) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `repository.py` with the arguments, from the folder
    `cwd`, the top of the user's repository, with rn's folder at `plugin_root`, and git and gh
    reached through `host`.

    - `new <words> <goal>`, the user's words and the goal as put, each one argument: 0 printing the
      new run's folder from `cwd`, as `worktree.new` makes it, named by `place.named` from today
      and the words, with rn's design tree best practice.
    - `find`: 0 printing each run that `worktree.paused` gives, its folder from `cwd` a line,
      newest first, and nothing where there's none.
    - `pause <run>`: 0 printing the hash that `push.pause` gives.
    - `put-up <run> <deliverable>`: 0 printing the URL that `push.put_up` gives.
    - `checks <run> <file>...`: 0 printing nothing where `commit_checks.findings` gives none, and 1
      with each finding a line.
    - `trial <run> <round>`, the Round's folder from `cwd`: 0 printing the folder that
      `trial.starting_state` makes.

    `<run>` is the run's folder, as `place.of_folder` takes it. 1 with `repository.py: <what's
    wrong>` where the input is Wrong or something is Missing, saying how to mend it; 2 with what
    stopped it where it CantRun; 2 with the usage where the arguments are other than these.
    """
    if not argv or argv[0] not in _ARITY:
        return 2, "", USAGE
    least, most = _ARITY[argv[0]]
    given = list(argv[1:])
    if len(given) < least or (most is not None and len(given) > most):
        return 2, "", USAGE
    try:
        return _SUBCOMMANDS[argv[0]](given, cwd, plugin_root, host)
    except (Wrong, Missing) as wrong:
        return 1, "", f"repository.py: {wrong}\n"
    except CantRun as stopped:
        return 2, "", f"repository.py: {stopped}\n"


def _new(given: list[str], cwd: str, plugin_root: str, host: Host) -> tuple[int, str, str]:
    words, goal = given
    run = place.RunPlace(cwd, place.named(date.today(), words))
    design_tree = practice.read(
        os.path.join(plugin_root, "domain", "best-practices", "design-tree")
    )
    made = worktree.new(run, goal, design_tree, host)
    return 0, f"{os.path.relpath(made.folder, cwd)}\n", ""


def _find(given: list[str], cwd: str, plugin_root: str, host: Host) -> tuple[int, str, str]:
    found = worktree.paused(cwd)
    return 0, "".join(f"{os.path.relpath(each.folder, cwd)}\n" for each in found), ""


def _pause(given: list[str], cwd: str, plugin_root: str, host: Host) -> tuple[int, str, str]:
    return 0, f"{push.pause(place.of_folder(cwd, given[0]), host)}\n", ""


def _put_up(given: list[str], cwd: str, plugin_root: str, host: Host) -> tuple[int, str, str]:
    return 0, f"{push.put_up(place.of_folder(cwd, given[0]), given[1], host)}\n", ""


def _checks(given: list[str], cwd: str, plugin_root: str, host: Host) -> tuple[int, str, str]:
    found = commit_checks.findings(place.of_folder(cwd, given[0]), given[1:], host)
    return (1 if found else 0), "".join(f"{each}\n" for each in found), ""


def _trial(given: list[str], cwd: str, plugin_root: str, host: Host) -> tuple[int, str, str]:
    run = place.of_folder(cwd, given[0])
    round_ = files.at(run, os.path.join(cwd, given[1]))
    return 0, f"{trial.starting_state(run, round_, host)}\n", ""


_SUBCOMMANDS: dict[str, Callable[[list[str], str, str, Host], tuple[int, str, str]]] = {
    "new": _new,
    "find": _find,
    "pause": _pause,
    "put-up": _put_up,
    "checks": _checks,
    "trial": _trial,
}
