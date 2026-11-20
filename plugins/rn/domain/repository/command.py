"""Decides repository.py's command line: its subcommands, what each takes and prints, and the exit
code by which whoever ran it reads its result."""

from __future__ import annotations

from collections.abc import Sequence

from repository.host import Host

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
    raise NotImplementedError("repository.command.main")
