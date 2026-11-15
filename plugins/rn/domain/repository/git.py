"""How repository runs git for tree.py, and reads what it prints: the worktree of a run, a commit,
and a push, each as one git command in a folder."""

from __future__ import annotations

from collections.abc import Sequence


def add_worktree(root: str, worktree: str, branch: str) -> None:
    """Makes rn's worktree of a run on a branch of its own.

    Takes: the repository's root, the worktree's folder, and the branch's name.
    Gives: nothing.
    Changes: runs `git worktree add -b <branch> <worktree>` at the root.
    Refuses: fault.Missing, where the root is no git repository; fault.CantRun, with what git said,
    where git fails otherwise.
    Carries: S1 `O->>T: makes the run's worktree`, as tree.py runs git through repository.
    """
    raise NotImplementedError("git.add_worktree")


def worktrees(root: str) -> tuple[tuple[str, str], ...]:
    """Each worktree of the repository, with its branch.

    Takes: the repository's root, or any folder in one of its worktrees.
    Gives: each worktree's folder and branch, from `git worktree list --porcelain`.
    Changes: nothing.
    Refuses: fault.Missing, where the folder lies in no git repository; fault.CantRun, where git
    fails otherwise.
    Carries: S5 `A->>T: gets the run of the worktree that holds the folder, or else the runs left`,
    and `O->>T: lists the runs left`.
    """
    raise NotImplementedError("git.worktrees")


def commit(worktree: str, paths: Sequence[str], message: str) -> str:
    """Commits the paths with the message.

    Takes: the worktree, each path from it to commit, and the message.
    Gives: the commit's ID, or the ID of HEAD where nothing changed.
    Changes: runs `git add` and `git commit` in the worktree.
    Refuses: fault.CantRun, with what git said, where git fails.
    Carries: S1 `K->>T: writes them, and commits`, `G->>T: commits its work at the end of each
    step`; S4 `T->>RP: commits, and pushes`.
    """
    raise NotImplementedError("git.commit")


def push(worktree: str, branch: str) -> None:
    """Pushes the branch to its remote.

    Takes: the worktree and its branch.
    Gives: nothing.
    Changes: runs `git push -u origin <branch>`.
    Refuses: fault.Missing, naming what's missing, where there's no remote or no login to push
    with; fault.CantRun, where git fails otherwise.
    Carries: S3 `T->>RP: pushes`, its `RP-->>T: what's missing`, and `RP->>GH: pushes`; S4 the same.
    """
    raise NotImplementedError("git.push")


def file_at(worktree: str, commit_id: str, path: str) -> str:
    """The text of a file as a commit holds it.

    Takes: the worktree, a commit's ID, and the file's path from the worktree.
    Gives: the file's text at that commit, from `git show <commit>:<path>`.
    Changes: nothing.
    Refuses: fault.CantRun, where the commit doesn't hold the file or git fails.
    Carries: S1 `T->>K` behind `alt no decision that answers the more's necessary condition changed
    since the round's cut`, as the round's cut is the tree as committed at the round's start.
    """
    raise NotImplementedError("git.file_at")
