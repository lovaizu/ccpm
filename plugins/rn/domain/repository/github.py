"""Decides each gh command that repository runs for tree.py on GitHub: whether gh is logged in, the
draft pull request of the run's branch, the user's comments on it, marking it ready, and the issue
of each lesson on rn's repository, each read from what gh prints as its manual and recorded runs
show."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

# The repository that each lesson the user signs off goes to as an issue.
RN_REPOSITORY = "lovaizu/ccpm"


@dataclass(frozen=True)
class PullRequest:
    """The pull request of a branch: its URL, and whether it's still a draft."""

    url: str
    draft: bool


@dataclass(frozen=True)
class Comment:
    """One comment on the pull request, with when it was made, as `createdAt` gives it."""

    body: str
    at: str


def logged_in(cwd: str, environ: Mapping[str, str]) -> None:
    """Raises Missing, with what gh said and that the user runs `gh auth login`, where
    `gh auth status` finds no login."""
    raise NotImplementedError("github.logged_in")


def pull_request(cwd: str, branch: str, environ: Mapping[str, str]) -> PullRequest | None:
    """The pull request of the branch, or None where gh finds none for it."""
    raise NotImplementedError("github.pull_request")


def open_draft(cwd: str, branch: str, title: str, environ: Mapping[str, str]) -> PullRequest:
    """Opens a draft pull request of the branch with the title, and gives it."""
    raise NotImplementedError("github.open_draft")


def comments(cwd: str, branch: str, since: str, environ: Mapping[str, str]) -> tuple[Comment, ...]:
    """Each comment on the branch's pull request made at or after the time `since`, in the order
    made."""
    raise NotImplementedError("github.comments")


def mark_ready(cwd: str, branch: str, environ: Mapping[str, str]) -> None:
    """Marks the branch's pull request ready for review."""
    raise NotImplementedError("github.mark_ready")


def open_issue(cwd: str, words: str, environ: Mapping[str, str]) -> str:
    """Opens an issue on rn's repository whose title is the first line of the words and whose body
    is the rest, and gives its URL."""
    raise NotImplementedError("github.open_issue")
