"""Decides tree.py's command line: its subcommands, what each takes and prints, and the exit code
by which whoever ran it reads its result."""

from __future__ import annotations

from collections.abc import Sequence

from repository.host import Host

USAGE = """\
usage: tree.py touched <run> [<pointer>]
       tree.py commit <run> <ground>
       tree.py cut <run> <role> <deliverable>
       tree.py signoff <run>
"""


def main(argv: Sequence[str], cwd: str, plugin_root: str, host: Host) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `tree.py` with the arguments, from the folder `cwd`,
    with rn's folder at `plugin_root`, and git reached through `host`.

    - `touched <run> <pointer>`: 0 printing each node that `tree.touched.touched` gives, its
      pointer a line, one word each, as Lane takes the lines as a checklist's items.
    - `touched <run>`: the same for each node that `tree.touched.changed` gives between the tree in
      the work branch's last commit and the tree as it stands, each node once, the changed nodes
      left out.
    - `commit <run> <ground>`: where `tree.checks.faults` finds none, commits the design tree as
      `push.commit` does with `<ground>` as the message, and gives 0 printing the hash; else 1
      with the first fault, git left as it was; 0 printing the last commit's hash, committing
      nothing, where the tree has no change since it.
    - `cut <run> <role> <deliverable>`, `<role>` `generator` or `evaluator`: writes the role's Cut
      in the Round that `rounds.course.next_of` gives the deliverable, made anew where the
      generator starts a new Round, and gives 0 printing the Cut's path from `cwd`; 1 where the
      deliverable waits on another role, the user, or the orchestrator, saying which.
    - `signoff <run>`: writes the tree that `tree.signoff.signed_off` gives for the deliverable
      that `tree.signoff.waiting` names, and gives 0 printing its path; 1 where none waits.

    `<run>` is the run's folder, as `place.of_folder` takes it. 1 with `tree.py: <what's wrong>`
    where the input is Wrong or something is Missing, saying how to mend it; 2 with what stopped it
    where it CantRun; 2 with the usage where the arguments are other than these.
    """
    raise NotImplementedError("tree.command.main")
