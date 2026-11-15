"""How repository runs gh for tree.py, and reads what it prints: the pull request of a branch, its
comments, and an issue, each as one gh command."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PullRequest:
    """The pull request of a run's branch: its URL, and whether it's a draft."""

    url: str
    draft: bool


@dataclass(frozen=True)
class Comment:
    """One comment of the user's on the pull request: who wrote it, when, where, and its words."""

    author: str
    at: str
    path: str
    body: str


def draft_pull_request(worktree: str, branch: str, title: str, body: str) -> PullRequest:
    """Opens the branch's draft pull request, or keeps the one open.

    Takes: the worktree, its branch, and the title and body that a new pull request takes.
    Gives: the branch's pull request.
    Changes: runs `gh pr create --draft` where the branch has none open.
    Refuses: fault.Missing, naming what's missing, where gh isn't logged in or the repository has no
    GitHub remote; fault.CantRun, where gh fails otherwise.
    Carries: S3 `T->>RP: pushes, and opens or keeps the draft pull request`, and `RP->>GH`.
    """
    raise NotImplementedError("gh.draft_pull_request")


def mark_ready(worktree: str, ready: bool) -> PullRequest:
    """Marks the branch's pull request ready, or a draft again.

    Takes: the worktree, and True for ready or False for a draft.
    Gives: the pull request as it now stands.
    Changes: runs `gh pr ready`, or `gh pr ready --undo`.
    Refuses: fault.Missing, where gh isn't logged in or the branch has no pull request;
    fault.CantRun, where gh fails otherwise.
    Carries: S6 `T->>RP: marks it ready`, `RP->>GH: marks it ready`, `T->>RP: marks it a draft
    again`, and `RP->>GH: marks it a draft`.
    """
    raise NotImplementedError("gh.mark_ready")


def comments(worktree: str, since: str) -> tuple[Comment, ...]:
    """The comments on the branch's pull request since a moment.

    Takes: the worktree, and the moment, in ISO 8601.
    Gives: each comment made after it, review comments among them, in the order made.
    Changes: nothing.
    Refuses: fault.Missing, where gh isn't logged in or the branch has no pull request;
    fault.CantRun, where gh fails otherwise.
    Carries: S3 `T->>RP: gets them`, `RP->>GH: reads them`, and `RP-->>T: the comments (Comment)`.
    """
    raise NotImplementedError("gh.comments")


def open_issue(repository: str, title: str, body: str) -> str:
    """Opens an issue on a repository.

    Takes: the repository, as `<owner>/<name>`, and the issue's title and body.
    Gives: the issue's URL.
    Changes: runs `gh issue create`.
    Refuses: fault.Missing, where gh isn't logged in; fault.CantRun, where gh fails otherwise.
    Carries: S7 `T->>RP: opens the issue on rn's repository (Sign-off)`, and `RP->>GH: opens the
    issue, with the lesson's words`.
    """
    raise NotImplementedError("gh.open_issue")
