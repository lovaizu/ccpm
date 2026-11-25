"""Decides which of the repository's own checks run on a generator's files, and how: the checks
that git runs before a commit, on those files alone, in the run's worktree, through an index of
their own, so that what another role staged is neither judged nor changed."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Mapping, Sequence

from fault import CantRun, Wrong

from repository.host import Host, Ran, checked
from repository.place import RunPlace

# The exit codes of a shell whose program can't be found or can't run.
_CANT_RUN = (126, 127)


def findings(run: RunPlace, files: Sequence[str], host: Host) -> list[str]:
    """What the repository's commit checks find in the files.

    Takes: the run, each file the generator wrote, from the worktree's top, and the host.
    Gives: each line that a check printed where one fails, in its order; none where each passes, or
    where the repository sets no check that git runs before a commit.
    Changes: nothing of the run's worktree or its index: the checks read an index of their own,
    of the branch's head and the files, as a commit of the files alone would hold, which is removed
    after them.
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
    with tempfile.TemporaryDirectory() as folder:
        alone = _with_index(host, os.path.join(folder, "index"))
        head = ["git", "read-tree", "HEAD"]
        checked(alone, head, run.worktree, CantRun, "git can't read the branch's head")
        add = ["git", "add", "--", *files]
        checked(alone, add, run.worktree, CantRun, "git can't stage the files")
        ran = alone(["git", "hook", "run", "--ignore-missing", "pre-commit"], run.worktree)
    said = [each for each in (ran.out + ran.err).splitlines() if each.strip()]
    if ran.code in _CANT_RUN:
        raise CantRun(f"the repository's commit check can't run: {' '.join(said)}")
    return said if ran.code != 0 else []


def _with_index(host: Host, index: str) -> Host:
    """The host, each git it runs, and each check that git runs, reading and writing the index at
    the path in place of the worktree's own."""

    def ran(argv: Sequence[str], cwd: str, env: Mapping[str, str] | None = None) -> Ran:
        return host(argv, cwd, {**(env or {}), "GIT_INDEX_FILE": index})

    return ran
