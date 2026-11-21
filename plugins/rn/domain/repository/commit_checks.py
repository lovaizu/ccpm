"""Decides which of the repository's own checks run on a generator's files, and how: the checks
that git runs before a commit, on those files alone, in the run's worktree."""

from __future__ import annotations

import os
from collections.abc import Sequence

from fault import CantRun, Wrong

from repository.host import Host, checked
from repository.place import RunPlace

# The exit codes of a shell whose program can't be found or can't run.
_CANT_RUN = (126, 127)


def findings(run: RunPlace, files: Sequence[str], host: Host) -> list[str]:
    """What the repository's commit checks find in the files.

    Takes: the run, each file the generator wrote, from the worktree's top, and the host.
    Gives: each line that a check printed where one fails, in its order; none where each passes, or
    where the repository sets no check that git runs before a commit.
    Changes: stages the files in the run's worktree, as the checks read what a commit would hold.
    Refuses: Wrong where a file lies outside the worktree or doesn't exist, naming it; CantRun
    where a check can't run, such as its program missing, with what it said.
    """
    for each in files:
        if not run.holds(each):
            raise Wrong(f"{each}: lies outside the run's worktree; give files from its top")
        if not os.path.exists(os.path.join(run.worktree, each)):
            raise Wrong(f"{each}: no such file in the run's worktree; give the files you wrote")
    if not files:
        return []
    checked(host, ["git", "add", "--", *files], run.worktree, CantRun, "git can't stage the files")
    ran = host(["git", "hook", "run", "--ignore-missing", "pre-commit"], run.worktree)
    said = [each for each in (ran.out + ran.err).splitlines() if each.strip()]
    if ran.code in _CANT_RUN:
        raise CantRun(f"the repository's commit check can't run: {' '.join(said)}")
    return said if ran.code != 0 else []
