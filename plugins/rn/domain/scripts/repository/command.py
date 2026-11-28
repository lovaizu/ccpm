"""Decides repository's command line: its subcommands, what each takes and prints, and the exit
code by which whoever ran it reads its result."""

from __future__ import annotations

import os
from collections.abc import Callable, Sequence
from datetime import date

from fault import Answer, answered
from host import Host
from place import WorkPlace, named, of_folder

from repository import trial, worktree

USAGE = """\
usage: repository new <slug>
       repository works
       repository trial <work> <round>
"""


def main(argv: Sequence[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    """The exit code, stdout, and stderr of `repository` with the arguments, from the folder
    `cwd`, a folder in the user's repository, with rn's folder at `plugin_root`, and git reached
    through `host`.

    - `new <slug>`, a short English slug of what the work is for: 0 printing the new work's folder,
      absolute, as `worktree.new` makes it at the top of the worktree that `cwd` lies in, named by
      `place.named` from today and the slug.
    - `works`: 0 printing the folder, absolute, of each piece of work that `worktree.left` gives,
      a line each, newest first, and nothing where there's none.
    - `trial <work> <round>`, the Round's folder from `cwd`: 0 printing the folder that
      `trial.starting_state` makes.

    `<work>` is the work's folder, as `place.of_folder` takes it. 1 with `repository: <what's
    wrong>` where the input is Wrong or something is Missing, saying how to mend it; 2 with what
    stopped it where it CantRun; 2 with the usage where the arguments are other than these.
    """
    if not argv or argv[0] not in _SUBCOMMANDS or len(argv) - 1 != _SUBCOMMANDS[argv[0]][1]:
        return 2, "", USAGE
    subcommand = _SUBCOMMANDS[argv[0]][0]
    return answered("repository", lambda: subcommand(list(argv[1:]), cwd, plugin_root, host))


def _new(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    made = worktree.new(WorkPlace(worktree.top(cwd, host), named(date.today(), given[0])))
    return 0, f"{made.folder}\n", ""


def _works(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    found = worktree.left(cwd, host, _schema(plugin_root))
    return 0, "".join(f"{each.folder}\n" for each in found), ""


def _schema(plugin_root: str) -> str:
    return os.path.join(plugin_root, "domain", "schemas", "steering.schema.json")


def _trial(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    work = of_folder(cwd, given[0])
    return 0, f"{trial.starting_state(work, os.path.join(cwd, given[1]), host)}\n", ""


_Subcommand = Callable[[list[str], str, str, Host], Answer]
# Each subcommand, with the count of arguments after its name.
_SUBCOMMANDS: dict[str, tuple[_Subcommand, int]] = {
    "new": (_new, 1),
    "works": (_works, 0),
    "trial": (_trial, 2),
}
