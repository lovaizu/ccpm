"""Decides how rn runs git on the run's worktree: which files a commit takes, and the message it
carries."""

from __future__ import annotations


def commit(top: str, run: str, ground: str) -> str:
    """Commits the run's folder.

    Takes: the top of the run's worktree, the run's folder within it, and the ground of the change.
    Gives: the commit's hash.
    Changes: the work's branch, by one commit of each change in the run's folder, with the ground
    word for word as its message.
    Refuses: Wrong where the ground is empty or the folder holds no change; Missing where `top`
    isn't a git repository; CantRun where git fails otherwise."""
    raise NotImplementedError("git.commit")
