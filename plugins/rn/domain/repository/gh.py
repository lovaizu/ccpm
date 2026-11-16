"""How repository runs gh for tree.py, and reads what it prints: the pull request of a branch, its
comments, and an issue, each as one gh command."""

from __future__ import annotations

import datetime
import json
import os
import subprocess
from dataclasses import dataclass
from typing import Any

from fault import CantRun, Missing

from repository import git


@dataclass(frozen=True)
class PullRequest:
    """The pull request of a run's branch: its URL, and whether it's a draft."""

    url: str
    draft: bool


@dataclass(frozen=True)
class Comment:
    """One comment of the user's on the pull request: who wrote it, when, the file and line it lies
    on, "" and None for one of the pull request's conversation, and its words."""

    author: str
    at: str
    path: str
    line: int | None
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
    _logged_in(worktree)
    viewed = _run(worktree, "pr", "view", branch, "--json", "url,isDraft")
    if viewed.returncode == 0:
        shown = json.loads(viewed.stdout)
        return PullRequest(shown["url"], shown["isDraft"])
    # Where view failed for want of a pull request, create opens one; where it failed otherwise,
    # create fails alike, and says why.
    made = _run(
        worktree, "pr", "create", "--draft", "--head", branch, "--title", title, "--body", body
    )
    # Runs only where gh pr create fails, which no line of the double's record holds; taken back to
    # the cases' designer.
    if made.returncode != 0:  # pragma: no cover
        raise CantRun(f"gh pr create failed: {made.stderr.strip()}")
    return PullRequest(made.stdout.strip(), True)


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
    _logged_in(worktree)
    branch = _branch(worktree)
    viewed = _run(worktree, "pr", "view", branch, "--json", "url")
    if viewed.returncode != 0:
        raise Missing(f"the branch {branch} has no pull request to mark; push it with tree.py push")
    _gh(worktree, "pr", "ready", branch, *(() if ready else ("--undo",)))
    return PullRequest(json.loads(viewed.stdout)["url"], not ready)


def comments(worktree: str, since: str) -> tuple[Comment, ...]:
    """The user's comments on the branch's pull request since a moment.

    Takes: the worktree, on the run's branch, and the moment, in ISO 8601 with its offset, such as
    `2026-11-15T09:00:00Z`.
    Gives: each comment made after it by the account gh is logged in as, which runs rn, leaving out
    every other author, bots among them: those of the pull request's conversation, from `gh pr view
    --json url,comments`, with the path "" and the line None, and its line comments, from `gh api
    --paginate --slurp repos/<owner>/<repository>/pulls/<number>/comments`, with the file's path and
    the line, None where the comment's line is no longer in the diff; all in the order made, each
    with its author's login, when it was made, and its words; none where no comment came after it.
    Changes: nothing.
    Refuses: fault.Missing, where gh isn't logged in or the branch has no pull request.
    Carries: S3 `T->>RP: gets them`, `RP->>GH: reads them`, and `RP-->>T: the comments (Comment)`.
    """
    _logged_in(worktree)
    branch = _branch(worktree)
    viewed = _run(worktree, "pr", "view", branch, "--json", "url,comments")
    # Runs only where the branch has no pull request, which tree.py push opens before any sign-off,
    # so no case reaches it; taken back to the cases' designer.
    if viewed.returncode != 0:  # pragma: no cover
        raise Missing(f"the branch {branch} has no pull request to read comments from")
    shown = json.loads(viewed.stdout)
    talk = [
        Comment(c["author"]["login"], c["createdAt"], "", None, c["body"])
        for c in shown["comments"]
    ]
    on_lines = [
        Comment(c["user"]["login"], c["created_at"], c["path"], c["line"], c["body"])
        for page in _pages(worktree, _review_comments_path(shown["url"]))
        for c in page
    ]
    user = _gh(worktree, "api", "user", "--jq", ".login").strip()
    after = _moment(since)
    each = [c for c in talk + on_lines if c.author == user and _moment(c.at) > after]
    return tuple(sorted(each, key=lambda c: _moment(c.at)))


def open_issue(repository: str, title: str, body: str) -> str:
    """Opens an issue on a repository.

    Takes: the repository, as `<owner>/<name>`, and the issue's title and body.
    Gives: the issue's URL.
    Changes: runs `gh issue create`.
    Refuses: fault.Missing, where gh isn't logged in; fault.CantRun, where gh fails otherwise.
    Carries: S7 `T->>RP: opens the issue on rn's repository (Sign-off)`, and `RP->>GH: opens the
    issue, with the lesson's words`.
    """
    here = os.getcwd()
    _logged_in(here)
    return _gh(
        here, "issue", "create", "--repo", repository, "--title", title, "--body", body
    ).strip()


def _run(worktree: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["gh", *args], cwd=worktree, capture_output=True, text=True, check=False)


def _review_comments_path(url: str) -> str:
    """The REST path of the line comments of the pull request at the URL, which ends in
    `<owner>/<repository>/pull/<number>`."""
    owner, repository, _, number = url.rstrip("/").split("/")[-4:]
    return f"repos/{owner}/{repository}/pulls/{number}/comments"


def _pages(worktree: str, path: str) -> list[list[dict[str, Any]]]:
    """Each page that `gh api --paginate --slurp` gives for the path, as one JSON list of pages."""
    return json.loads(_gh(worktree, "api", "--paginate", "--slurp", path))


def _gh(worktree: str, *args: str) -> str:
    """What gh printed for the command; raises CantRun, with what gh said, where it fails."""
    done = _run(worktree, *args)
    # Runs only where gh fails after its login was found, which no line of the double's record
    # holds; taken back to the cases' designer.
    if done.returncode != 0:  # pragma: no cover
        raise CantRun(f"gh {args[0]} failed: {done.stderr.strip()}")
    return done.stdout


def _branch(worktree: str) -> str:
    """The branch that the worktree is on, as `repository.git.worktrees` lists it."""
    here = os.path.realpath(worktree)
    return next(branch for folder, branch in git.worktrees(worktree) if folder == here)


def _moment(text: str) -> datetime.datetime:
    """A moment in ISO 8601, `Z` for UTC as gh and tree.py write it, which Python 3.9's
    fromisoformat doesn't read."""
    return datetime.datetime.fromisoformat(text.replace("Z", "+00:00"))


def _logged_in(worktree: str) -> None:
    """Raises Missing where gh is logged in to no account, as no command of it can then change
    GitHub."""
    if _run(worktree, "auth", "status").returncode != 0:
        raise Missing("gh isn't logged in to GitHub; log in with `gh auth login`")
