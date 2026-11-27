"""Decides repository's command line: its subcommands, what each takes and prints, and the exit
code by which whoever ran it reads its result."""

from __future__ import annotations

import os
from collections.abc import Callable, Sequence
from datetime import date

import form
import push
from fault import Answer, Wrong, answered
from host import Host
from place import WorkPlace, named, of_folder

from repository import trial, worktree

USAGE = """\
usage: repository new <slug> <worktree> made|users
       repository works
       repository stop <work>
       repository cancel <work>
       repository trial <work> <round>
"""


def main(argv: Sequence[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    """The exit code, stdout, and stderr of `repository` with the arguments, from the folder
    `cwd`, a folder in the user's repository, with rn's folder at `plugin_root`, and git and gh
    reached through `host`.

    - `new <slug> <worktree> made|users`, a short English slug of what the work is for, the
      worktree it's made in, from `cwd` or absolute, and whether that worktree was made for the work
      or is the user's own: 0 printing the new work's folder, absolute, as `worktree.new` makes it,
      named by `place.named` from today and the slug.
    - `works`: 0 printing the folder, absolute, of each piece of work that `worktree.left` gives,
      a line each, newest first, and nothing where there's none.
    - `stop <work>`: 0 printing the hash that `push.stop` gives, with the work's steering, read as
      its schema holds it, where it has one.
    - `cancel <work>`: 0 printing each thing of the work that `worktree.removed` removed on GitHub
      once it removes the work here, a line each, and nothing where there's none; and on stderr
      `repository: can't remove <what, and why>` for each thing that it couldn't ask GitHub of
      or remove there, a line each; it removes the work's trials' folders as `trial.removed` does.
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
    if given[2] not in ("made", "users"):
        raise Wrong(f"{given[2]!r} says neither whose the worktree is; give made or users")
    where = os.path.normpath(os.path.join(cwd, given[1]))
    made = worktree.new(WorkPlace(where, named(date.today(), given[0])), host, given[2] == "users")
    return 0, f"{made.folder}\n", ""


def _works(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    return 0, "".join(f"{each.folder}\n" for each in worktree.left(cwd, host)), ""


def _stop(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    work = of_folder(cwd, given[0])
    schema = os.path.join(plugin_root, "domain", "schemas", "steering.schema.json")
    steering = (
        form.held(work.steering, schema, "the steering") if os.path.isfile(work.steering) else None
    )
    return 0, f"{push.stop(work, steering, host)}\n", ""


def _cancel(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    work = of_folder(cwd, given[0])
    gone = worktree.removed(work, host)
    trial.removed(work)
    said = "".join(f"repository: can't remove {each}\n" for each in gone.kept)
    return 0, "".join(f"{each}\n" for each in gone.removed), said


def _trial(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    work = of_folder(cwd, given[0])
    return 0, f"{trial.starting_state(work, os.path.join(cwd, given[1]), host)}\n", ""


_Subcommand = Callable[[list[str], str, str, Host], Answer]
# Each subcommand, with the count of arguments after its name.
_SUBCOMMANDS: dict[str, tuple[_Subcommand, int]] = {
    "new": (_new, 3),
    "works": (_works, 0),
    "stop": (_stop, 1),
    "cancel": (_cancel, 1),
    "trial": (_trial, 2),
}
