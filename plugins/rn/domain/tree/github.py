"""Decides what a run shows on GitHub: the work's pull request, a draft until the work is handed
over and again once it's sent back, the user's comments on it since a sign-off, and the issue of
each lesson the user signs off on rn's repository."""

from __future__ import annotations

from repository.gh import Comment, PullRequest

from tree.runs import Run


def keep_draft(run: Run) -> PullRequest:
    """Opens the run's draft pull request, or keeps the one open.

    Takes: the run.
    Gives: the pull request.
    Changes: through `repository.gh.draft_pull_request`, with the goal as its title.
    Refuses: fault.Missing, naming what's missing, where gh can't open it.
    Carries: S3 `T->>RP: pushes, and opens or keeps the draft pull request`.
    """
    raise NotImplementedError("github.keep_draft")


def hand_over(run: Run, ready: bool) -> PullRequest:
    """Marks the run's pull request ready, or a draft again.

    Takes: the run, and True to hand the work over or False as the user sends it back.
    Gives: the pull request.
    Changes: through `repository.gh.mark_ready`.
    Refuses: fault.Missing, naming what's missing, where gh can't mark it.
    Carries: S6 `O->>T: marks the pull request ready`, `T->>RP: marks it ready`, and `T->>RP: marks
    it a draft again`.
    """
    raise NotImplementedError("github.hand_over")


def comments(run: Run, since: str) -> tuple[Comment, ...]:
    """The user's comments on the run's pull request since a sign-off.

    Takes: the run, and when the sign-off was put up, in ISO 8601.
    Gives: each comment since then.
    Changes: nothing.
    Refuses: fault.Missing, naming what's missing, where gh can't read them.
    Carries: S3 `O->>T: gets the user's comments since the sign-off`, `T->>RP: gets them`, and
    `T-->>O: the comments (Comment)`.
    """
    raise NotImplementedError("github.comments")


def open_lesson(plugin_root: str, lesson: str) -> str:
    """Opens the issue of a lesson on rn's repository.

    Takes: rn's folder, whose manifest names its repository, and the lesson's words.
    Gives: the issue's URL.
    Changes: through `repository.gh.open_issue`, with the lesson's words as they were signed off.
    Refuses: fault.Missing, naming what's missing, where gh can't open it.
    Carries: S7 `T->>RP: opens the issue on rn's repository (Sign-off)`.
    """
    raise NotImplementedError("github.open_lesson")
