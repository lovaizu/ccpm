"""How repository runs git for tree.py, and reads what it prints: the worktree of a run, a commit,
and a push, each as one git command in a folder."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Sequence

from fault import CantRun, Missing

# What git says where a folder lies in no repository.
_NO_REPOSITORY = "not a git repository"
# What git says where it has no login to push with.
_NO_LOGIN = ("could not read Username", "Authentication failed", "Permission denied")


def add_worktree(root: str, worktree: str, branch: str) -> None:
    """Makes rn's worktree of a run on a branch of its own.

    Takes: the repository's root, the worktree's folder, and the branch's name.
    Gives: nothing.
    Changes: runs `git worktree add -b <branch> <worktree>` at the root.
    Refuses: fault.Missing, where the root is no git repository; fault.CantRun, with what git said,
    where git fails otherwise.
    Carries: S1 `O->>T: makes the run's worktree`, as tree.py runs git through repository.
    """
    _git(root, "worktree", "add", "-q", "-b", branch, worktree)


def worktrees(root: str) -> tuple[tuple[str, str], ...]:
    """Each worktree of the repository, with its branch.

    Takes: the repository's root, or any folder in one of its worktrees.
    Gives: each worktree's folder, as its real path, and branch, from `git worktree list
    --porcelain`, the repository's own first, and "" as the branch of one on no branch.
    Changes: nothing.
    Refuses: fault.Missing, where the folder lies in no git repository; fault.CantRun, where git
    fails otherwise.
    Carries: S5 `A->>T: gets the run of the worktree that holds the folder, or else the runs left`,
    and `O->>T: lists the runs left`.
    """
    found: list[tuple[str, str]] = []
    for line in _git(root, "worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            found.append((os.path.realpath(line[len("worktree ") :]), ""))
        elif line.startswith("branch refs/heads/") and found:
            found[-1] = (found[-1][0], line[len("branch refs/heads/") :])
    return tuple(found)


def commit(worktree: str, paths: Sequence[str], message: str) -> str:
    """Commits the paths with the message.

    Takes: the worktree, each path from it to commit, `.` for all of it, and the message, kept word
    for word.
    Gives: the commit's ID, or the ID of HEAD where nothing changed.
    Changes: runs `git add` and `git commit` in the worktree.
    Refuses: fault.CantRun, with what git said, where git fails, such as on a path that isn't there.
    Carries: S1 `K->>T: writes them, and commits`, `G->>T: commits its work at the end of each
    step`; S4 `T->>RP: commits, and pushes`.
    """
    _git(worktree, "add", "-A", "--", *paths)
    staged = subprocess.run(
        ["git", "-C", worktree, "diff", "--cached", "--quiet", "--", *paths], check=False
    )
    if staged.returncode != 0:
        _git(worktree, "commit", "-q", "--cleanup=verbatim", "-m", message, "--", *paths)
    return _git(worktree, "rev-parse", "HEAD").strip()


def changed(worktree: str) -> tuple[str, ...]:
    """Each file of the worktree that differs from its last commit.

    Takes: the worktree.
    Gives: each file's path from the worktree, new files among them, in git's order.
    Changes: nothing.
    Refuses: fault.CantRun, where git fails.
    Carries: S1 `G->>T: commits its work at the end of each step (Place)`, whose Place names the
    files of the work.
    """
    printed = _git(worktree, "status", "--porcelain", "-uall", "-z")
    return tuple(entry[3:] for entry in printed.split("\0") if len(entry) > 3)


def push(worktree: str, branch: str) -> None:
    """Pushes the branch to its remote.

    Takes: the worktree and its branch.
    Gives: nothing.
    Changes: runs `git push -u origin <branch>`.
    Refuses: fault.Missing, naming what's missing, where there's no remote or no login to push
    with; fault.CantRun, where git fails otherwise.
    Carries: S3 `T->>RP: pushes`, its `RP-->>T: what's missing`, and `RP->>GH: pushes`; S4 the same.
    """
    if "origin" not in _git(worktree, "remote").split():
        raise Missing(
            "the repository has no remote origin to push the work to; add one with"
            " `git remote add origin <url>`"
        )
    done = _run(worktree, "push", "-q", "-u", "origin", branch)
    # Runs only where a remote host asks for a login, which no case reaches, as the tests push to a
    # folder; taken back to the cases' designer.
    if done.returncode != 0 and any(each in done.stderr for each in _NO_LOGIN):  # pragma: no cover
        raise Missing(f"git has no login to push to origin: {done.stderr.strip()}")
    if done.returncode != 0:
        raise CantRun(f"git push failed: {done.stderr.strip()}")


def history(worktree: str, path: str) -> tuple[tuple[str, str], ...]:
    """Each commit that changed a file, with its message.

    Takes: the worktree, and the file's path from it.
    Gives: each commit's ID and its message word for word, the latest first; none where no commit
    holds the file.
    Changes: nothing.
    Refuses: fault.CantRun, where git fails.
    Carries: S1 `A->>T: ... the Cut`, which gives each decision with its ground, the message of the
    commit that made it.
    """
    printed = _git(worktree, "log", "--format=%H%x00%B%x00", "--", path)
    parts = printed.split("\0")
    return tuple((parts[i].strip(), parts[i + 1].rstrip("\n")) for i in range(0, len(parts) - 1, 2))


def file_at(worktree: str, commit_id: str, path: str) -> str:
    """The text of a file as a commit holds it.

    Takes: the worktree, a commit's ID, and the file's path from the worktree.
    Gives: the file's text at that commit, from `git show <commit>:<path>`.
    Changes: nothing.
    Refuses: fault.CantRun, where the commit doesn't hold the file or git fails.
    Carries: S1 `T->>K` behind `alt the decision that the more names didn't change
    since the round's cut`, as the round's cut is the tree as committed at the round's start.
    """
    return _git(worktree, "show", f"{commit_id}:{path}")


def _run(folder: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", folder, *args], capture_output=True, text=True, check=False)


def _git(folder: str, *args: str) -> str:
    """What git printed for the command in the folder; raises Missing where the folder lies in no
    repository, and CantRun, with what git said, where git fails otherwise."""
    done = _run(folder, *args)
    if done.returncode != 0 and _NO_REPOSITORY in done.stderr:
        raise Missing(f"{folder} lies in no git repository, which rn works in")
    if done.returncode != 0:
        raise CantRun(f"git {args[0]} failed in {folder}: {done.stderr.strip()}")
    return done.stdout
