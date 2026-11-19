"""Decides how rn runs git on the run's worktree: which files a commit takes, and the message it
carries."""

from __future__ import annotations

import subprocess

from fault import Missing, Wrong


def commit(top: str, run: str, ground: str) -> str:
    """Commits the run's folder.

    Takes: the top of the run's worktree, the run's folder within it, and the ground of the change.
    Gives: the commit's hash.
    Changes: the work's branch, by one commit of each change in the run's folder, with the ground
    word for word as its message.
    Refuses: Wrong where the ground is empty or the folder holds no change; Missing where `top`
    isn't a git repository. Where git fails otherwise, its CalledProcessError stops the command
    with git's trace."""
    if not ground.strip():
        raise Wrong("the ground is empty: give why the change decides as it does")
    if _git(top, "rev-parse", "--git-dir").returncode != 0:
        raise Missing(f"{top} is no git repository, which the run's worktree must be")
    _run(top, "add", "-A", "--", run)
    if _git(top, "diff", "--cached", "--quiet", "--", run).returncode == 0:
        raise Wrong(f"{run} holds no change to commit")
    _run(top, "commit", "-q", "-m", ground, "--", run)
    return _run(top, "rev-parse", "HEAD").strip()


def _git(top: str, *args: str) -> subprocess.CompletedProcess[str]:
    """git run with the arguments in `top`, as it ended."""
    return subprocess.run(["git", "-C", top, *args], capture_output=True, text=True, check=False)


def _run(top: str, *args: str) -> str:
    """What git prints, run with the arguments in `top`."""
    done = _git(top, *args)
    done.check_returncode()
    return done.stdout
