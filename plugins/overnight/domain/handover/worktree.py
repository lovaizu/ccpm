"""Where a piece's worktree lies and which branch it's on, as git keeps them:
`../<repository>-overnight-<n>/` on the branch `overnight/<n>`."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Worktree:
    """The folder and the branch where a piece works."""

    folder: str
    branch: str


class Refused(Exception):
    """git refused to make a piece's worktree, with git's words."""


def taken(repository: str) -> int:
    """The highest number that a branch or a worktree of overnight holds in the repository.

    Takes: the repository's root.
    Gives: the highest number of a branch `overnight/<n>` or a folder
    `../<repository>-overnight-<n>/`, or 0 where there is none.
    Changes: nothing.
    Refuses: Refused, with git's words, where git can't list them.
    """
    raise NotImplementedError("handover.worktree.taken")


def make(repository: str, number: int) -> Worktree:
    """Makes the piece's folder from the current commit, on a branch of its own.

    Takes: the repository's root and the piece's number.
    Gives: the piece's folder and branch.
    Changes: adds the worktree and its branch to the repository.
    Refuses: Refused, with git's words, where git can't make them.
    """
    raise NotImplementedError("handover.worktree.make")
