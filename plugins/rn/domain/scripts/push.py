"""Decides how the work reaches GitHub: each commit pushed at once, a commit kept for the next
push where the push is refused, and the work kept on a stop."""

from __future__ import annotations

from collections.abc import Sequence

from fault import CantRun, Missing
from host import Host, Ran, checked
from place import WorkPlace

# What git says where origin refuses a push for want of a login or a permission, in lower case:
# a remote that rejects the refs, as a folder that may not be written does, among them.
_REFUSED = ("permission", "could not read username", "authentication failed", "remote rejected")


def stop(work: WorkPlace, host: Host) -> str:
    """Keeps the work where any conversation picks it up.

    Takes: the work, and the host.
    Gives: the hash of the commit that the branch's remote now holds.
    Changes: commits each change in the work's worktree as `rn: stopped <name>`, where there's
    one, and pushes the work's branch, as `push` does.
    Refuses: as `push` refuses, as a stop that GitHub doesn't hold loses the work to any other
    conversation; CantRun where git fails otherwise.
    """
    _commit(work, f"rn: stopped {work.name}", None, host)
    return push(work, host)


def kept(work: WorkPlace, message: str, paths: Sequence[str] | None, host: Host) -> str:
    """Commits the work's changes and pushes them at once, so that nothing it makes lies only on
    the user's computer.

    Takes: the work, the commit's message, the paths to commit, or None for each change in the
    work's worktree, and the host.
    Gives: "" where the branch's remote now holds the commit; else what git said where it couldn't
    push, the commit kept, so that the next push carries it, as a check of the repository's may
    refuse a push until a later Round mends what it found.
    Changes: commits the changes with the message, where there's one, and pushes the work's branch,
    as `push` does.
    Refuses: Missing as `push` refuses; CantRun where git fails otherwise than on the push.
    """
    _commit(work, message, paths, host)
    try:
        push(work, host)
    except CantRun as why:
        return str(why)
    return ""


def _commit(work: WorkPlace, message: str, paths: Sequence[str] | None, host: Host) -> None:
    """Commits the changes of the paths, or each change in the work's worktree, with the message,
    where there's one."""
    _git(host, work, "add", "-A", *(["--", *paths] if paths is not None else []))
    if host(["git", "diff", "--cached", "--quiet"], work.worktree).code != 0:
        _git(host, work, "commit", "-q", "-m", message)


def push(work: WorkPlace, host: Host) -> str:
    """Pushes the work's branch to origin.

    Takes: the work, and the host.
    Gives: the hash of the commit that the branch's remote now holds.
    Changes: pushes the work's branch to `origin`, setting it upstream.
    Refuses: Missing where the repository has no remote `origin`, or the push is refused for want
    of a login or a permission, with what git said; CantRun where git fails otherwise.
    """
    if host(["git", "remote", "get-url", "origin"], work.worktree).code != 0:
        raise Missing("the repository has no remote origin to push the work to; add one")
    pushed = host(["git", "push", "-q", "-u", "origin", branch(work, host)], work.worktree)
    if pushed.code != 0 and any(each in pushed.err.lower() for each in _REFUSED):
        raise Missing(
            "origin refuses the push of the work, for want of a login or a permission:"
            f" {pushed.err.strip()}"
        )
    if pushed.code != 0:
        raise CantRun(f"git can't push the work: {pushed.err.strip()}")
    return _git(host, work, "rev-parse", "HEAD").out.strip()


def branch(work: WorkPlace, host: Host) -> str:
    """The work's branch, the one that the work's worktree has checked out.

    Takes: the work, and the host.
    Gives: the branch's name.
    Changes: nothing.
    Refuses: CantRun where git can't name it, with what it said.
    """
    return _git(host, work, "branch", "--show-current").out.strip()


def _git(host: Host, work: WorkPlace, *words: str) -> Ran:
    """Runs git in the work's worktree, raising CantRun with what it said where it fails."""
    return checked(host, ["git", *words], work.worktree, CantRun, f"git {words[0]} fails")
