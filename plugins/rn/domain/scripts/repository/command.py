"""Decides repository's command line: its subcommands, what each takes and prints, and the exit
code by which whoever ran it reads its result."""

from __future__ import annotations

import os
from collections.abc import Callable, Sequence
from datetime import date

import form
from fault import Answer, answered
from host import Host
from place import RunPlace, named, of_folder

from repository import push, trial, worktree

USAGE = """\
usage: repository new <slug>
       repository runs
       repository stop <run>
       repository cancel <run>
       repository put-up <run> <deliverable>
       repository trial <run> <round>
       repository diff <run>
"""


def main(argv: Sequence[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    """The exit code, stdout, and stderr of `repository` with the arguments, from the folder
    `cwd`, the top of the user's repository, with rn's folder at `plugin_root`, and git and gh
    reached through `host`.

    - `new <slug>`, a short English slug of the work: 0 printing the new run's folder from `cwd`,
      as `worktree.new` makes it, named by `place.named` from today and the slug.
    - `runs`: 0 printing the folder from `cwd` of each run that `worktree.found` gives, a line
      each, newest first, and nothing where there's none; and on stderr `repository: can't check
      <what, and why>` where it couldn't ask GitHub for the runs it holds.
    - `stop <run>`: 0 printing the hash that `push.stop` gives.
    - `cancel <run>`: 0 printing each thing of the run that `worktree.removed` removed on GitHub
      once it removes the run here, a line each, and nothing where there's none; and on stderr
      `repository: can't remove <what, and why>` for each thing that it couldn't ask GitHub of
      or remove there, a line each.
    - `put-up <run> <deliverable>`: 0 printing the link that `push.put_up` gives, from the run's
      steering, read as its schema holds it.
    - `trial <run> <round>`, the Round's folder from `cwd`: 0 printing the folder that
      `trial.starting_state` makes.
    - `diff <run>`: 0 printing the diff that `push.diff` gives.

    `<run>` is the run's folder, as `place.of_folder` takes it. 1 with `repository: <what's
    wrong>` where the input is Wrong or something is Missing, saying how to mend it; 2 with what
    stopped it where it CantRun; 2 with the usage where the arguments are other than these.
    """
    if not argv or argv[0] not in _SUBCOMMANDS or len(argv) - 1 != _SUBCOMMANDS[argv[0]][1]:
        return 2, "", USAGE
    subcommand = _SUBCOMMANDS[argv[0]][0]
    return answered("repository", lambda: subcommand(list(argv[1:]), cwd, plugin_root, host))


def _new(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    made = worktree.new(RunPlace(cwd, named(date.today(), given[0])), host)
    return 0, f"{os.path.relpath(made.folder, cwd)}\n", ""


def _runs(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    found = worktree.found(cwd, host)
    printed = "".join(f"{os.path.relpath(each.folder, cwd)}\n" for each in found.runs)
    said = f"repository: can't check {found.unchecked}\n" if found.unchecked else ""
    return 0, printed, said


def _stop(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    return 0, f"{push.stop(of_folder(cwd, given[0]), host)}\n", ""


def _cancel(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    gone = worktree.removed(of_folder(cwd, given[0]), host)
    said = "".join(f"repository: can't remove {each}\n" for each in gone.kept)
    return 0, "".join(f"{each}\n" for each in gone.removed), said


def _put_up(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    run = of_folder(cwd, given[0])
    schema = os.path.join(plugin_root, "domain", "schemas", "steering.schema.json")
    steering = form.held(run.steering, schema, "the steering")
    return 0, "".join(f"{each}\n" for each in push.put_up(run, steering, given[1], host)), ""


def _trial(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    run = of_folder(cwd, given[0])
    return 0, f"{trial.starting_state(run, os.path.join(cwd, given[1]), host)}\n", ""


def _diff(given: list[str], cwd: str, plugin_root: str, host: Host) -> Answer:
    return 0, push.diff(of_folder(cwd, given[0]), host), ""


_Subcommand = Callable[[list[str], str, str, Host], Answer]
# Each subcommand, with the count of arguments after its name.
_SUBCOMMANDS: dict[str, tuple[_Subcommand, int]] = {
    "new": (_new, 1),
    "runs": (_runs, 0),
    "stop": (_stop, 1),
    "cancel": (_cancel, 1),
    "put-up": (_put_up, 2),
    "trial": (_trial, 2),
    "diff": (_diff, 1),
}
