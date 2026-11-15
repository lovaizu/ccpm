"""Decides what tree.py commits on the work's branch, when, and with what message, and when it
pushes, through repository."""

from __future__ import annotations

from collections.abc import Sequence

from tree.runs import Run


def commit(run: Run, paths: Sequence[str], message: str) -> str:
    """Commits the run's files.

    Takes: the run, each path from the worktree to commit, and the commit's message: a decision's
    ground, or the step that ended.
    Gives: the commit's ID.
    Changes: commits through `repository.git.commit`, with the message word for word, so that the
    user finds a decision's ground in git.
    Refuses: fault.CantRun, where git fails.
    Carries: S1 `K->>T: writes them, and commits them with each decision's ground as the message`,
    `G->>T: commits its work at the end of each step`; S4 `O->>T: commits and pushes each role's
    work so far`.
    """
    raise NotImplementedError("branch.commit")


def push(run: Run) -> None:
    """Pushes the work's branch.

    Takes: the run.
    Gives: nothing.
    Changes: pushes through `repository.git.push`.
    Refuses: fault.Missing, naming what's missing, where git can't push.
    Carries: S3 `O->>T: pushes the work`, `T->>RP: pushes`, and `T-->>O: what's missing`; S4 the
    same.
    """
    raise NotImplementedError("branch.push")
