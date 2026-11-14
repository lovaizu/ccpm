"""Decides each git command that repository runs for tree.py on the user's repository, and how it
reads what git prints: a run's worktree and branch made from the checkout's HEAD, each worktree that
git lists, each commit of the run's work, and each push of its branch."""

from __future__ import annotations

from collections.abc import Mapping


def make_worktree(root: str, worktree: str, branch: str, environ: Mapping[str, str]) -> None:
    """Makes the worktree at the path on a new branch of the name, from the HEAD of the repository
    at the root. Raises Wrong where the branch or the worktree already exists."""
    raise NotImplementedError("repository.make_worktree")


def worktrees(root: str, environ: Mapping[str, str]) -> tuple[tuple[str, str], ...]:
    """Each worktree of the repository at the root that git lists, as its whole path and its
    branch."""
    raise NotImplementedError("repository.worktrees")


def commit(worktree: str, message: str, environ: Mapping[str, str]) -> bool:
    """Commits each change in the worktree with the message, and gives whether there was one to
    commit."""
    raise NotImplementedError("repository.commit")


def push(worktree: str, branch: str, environ: Mapping[str, str]) -> None:
    """Pushes the branch to the worktree's remote `origin`, setting it upstream. Raises Missing,
    with what git said and what the user clears, where the worktree has no `origin` or git can't
    push to it."""
    raise NotImplementedError("repository.push")
