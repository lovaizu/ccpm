"""Decides repository.py's command line: its subcommands, what each takes and prints, and the exit
code by which whoever ran it reads its result."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from datetime import date
from typing import Callable

import practice
from fault import Answer, answered
from rounds import files
from tree import form

from repository import commit_checks, place, push, trial, worktree
from repository.host import Host

USAGE = """\
usage: repository.py new <words> <goal> <deliverables language> <conversation language>
       repository.py find
       repository.py pause <run>
       repository.py put-up <run> <deliverable>
       repository.py checks <run> <file>...
       repository.py trial <run> <round>
"""


def main(argv: Sequence[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    """The exit code, stdout, and stderr of `repository.py` with the arguments, from the folder
    `cwd`, the top of the user's repository, with rn's folder at `plugin_root`, and git and gh
    reached through `host`.

    - `new <words> <goal> <deliverables language> <conversation language>`, the user's words, the
      goal as put, and the languages that the user settled, each one argument: 0 printing the new
      run's folder from `cwd`, as `worktree.new` makes it, named by `place.named` from today and
      the words, with the context that `tree.form.context` gives for rn's version, from
      `.claude-plugin/plugin.json` under `plugin_root`, and the languages, and with rn's design
      tree best practice.
    - `find`: 0 printing the folder from `cwd` of the run that `worktree.found` gives, its
      worktree made again where none lies, as a line, and nothing where there's none.
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
    if not argv or argv[0] not in _SUBCOMMANDS:
        return 2, "", USAGE
    subcommand, least, most = _SUBCOMMANDS[argv[0]]
    given = list(argv[1:])
    if len(given) < least or (most is not None and len(given) > most):
        return 2, "", USAGE
    return answered("repository.py", lambda: subcommand(given, cwd, plugin_root, host))


def _new(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    words, goal, deliverables, conversation = given
    run = place.RunPlace(cwd, place.named(date.today(), words))
    context = form.context(_version(plugin_root), deliverables, conversation)
    design_tree = practice.read(
        os.path.join(plugin_root, "domain", "best-practices", "design-tree")
    )
    made = worktree.new(run, context, goal, design_tree, host)
    return 0, f"{os.path.relpath(made.folder, cwd)}\n", ""


def _version(plugin_root: str) -> str:
    """rn's version, as its plugin.json gives it."""
    with open(os.path.join(plugin_root, ".claude-plugin", "plugin.json"), encoding="utf-8") as file:
        return json.load(file)["version"]


def _find(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    found = worktree.found(cwd, host)
    return 0, f"{os.path.relpath(found.folder, cwd)}\n" if found else "", ""


def _pause(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    return 0, f"{push.pause(place.of_folder(cwd, given[0]), host)}\n", ""


def _put_up(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    return 0, f"{push.put_up(place.of_folder(cwd, given[0]), given[1], host)}\n", ""


def _checks(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    found = commit_checks.findings(place.of_folder(cwd, given[0]), given[1:], host)
    return (1 if found else 0), "".join(f"{each}\n" for each in found), ""


def _trial(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    run = place.of_folder(cwd, given[0])
    round_ = files.at(run, os.path.join(cwd, given[1]))
    return 0, f"{trial.starting_state(run, round_, host)}\n", ""


_Subcommand = Callable[[list[str], str, str, Host], Answer]
# Each subcommand, with its least and most count of arguments after its name, None where it takes
# any more.
_SUBCOMMANDS: dict[str, tuple[_Subcommand, int, int | None]] = {
    "new": (_new, 4, 4),
    "find": (_find, 0, 0),
    "pause": (_pause, 1, 1),
    "put-up": (_put_up, 2, 2),
    "checks": (_checks, 1, None),
    "trial": (_trial, 2, 2),
}
