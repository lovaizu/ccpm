"""Decides which of the repository's own checks run on a generator's files, and how: the checks
that git runs before a commit, on those files alone, in the run's worktree."""

from __future__ import annotations

from collections.abc import Sequence

from repository.host import Host
from repository.place import RunPlace


def findings(run: RunPlace, files: Sequence[str], host: Host) -> list[str]:
    """What the repository's commit checks find in the files.

    Takes: the run, each file the generator wrote, from the worktree's top, and the host.
    Gives: each line that a check printed where one fails, in its order; none where each passes, or
    where the repository sets no check that git runs before a commit.
    Changes: stages the files in the run's worktree, as the checks read what a commit would hold.
    Refuses: Wrong where a file lies outside the worktree or doesn't exist, naming it; CantRun
    where a check can't run, such as its program missing, with what it said.
    """
    raise NotImplementedError("repository.commit_checks.findings")
