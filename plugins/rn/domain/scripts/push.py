"""Decides how the work reaches GitHub: each commit pushed at once, the work's one pull
request, a draft until the user marks it ready, opened once a need is picked, and the work
kept on a stop."""

from __future__ import annotations

import json
from typing import Any

from fault import CantRun, Missing
from host import Host, Ran, checked
from place import WorkPlace

# What git says where origin refuses a push for want of a login or a permission, in lower case:
# a remote that rejects the refs, as a folder that may not be written does, among them.
_REFUSED = (
    "permission to ",
    "permission denied (publickey",
    "could not read username",
    "authentication failed",
    "remote rejected",
)


def stop(work: WorkPlace, steering: dict[str, Any] | None, host: Host) -> str:
    """Keeps the work where any conversation picks it up.

    Takes: the work, its steering, or None where it has none yet, and the host.
    Gives: the hash of the commit that the branch's remote now holds.
    Changes: commits and pushes as `kept` does, as `rn: stopped <name>`.
    Refuses: as `kept` refuses.
    """
    return kept(work, steering, f"rn: stopped {work.name}", host)


def kept(work: WorkPlace, steering: dict[str, Any] | None, message: str, host: Host) -> str:
    """Commits each change of the work and pushes it at once, so that nothing it makes lies only
    on the user's computer.

    Takes: the work, its steering, or None where it has none yet, the commit's message, and the
    host.
    Gives: the hash of the commit that the branch's remote now holds.
    Changes: commits each change in the work's worktree with the message, where there's one, and
    pushes the work's branch, as `push` does; then, where the steering names a picked need and
    the branch has no pull request open, opens one into the default branch as a draft, as `gh pr
    view` gives a closed or merged one of an earlier work of the same branch's name too: titled by
    the words of the picked need, its body the work's outcome, then a line `Closes #N` for each
    issue that the work closes and a line `Refs #N` for each it refers to, in their order.
    Refuses: as `push` refuses; Missing, after the push, where `gh auth status` finds no login,
    or gh may not open the pull request, with what gh said; CantRun where gh can't tell whether
    the branch has a pull request, so that it never opens a second, or where git or gh fails
    otherwise.
    """
    _commit_all(work, message, host)
    pushed = push(work, host)
    if steering is not None:
        _pull_request(work, steering, host)
    return pushed


def _pull_request(work: WorkPlace, steering: dict[str, Any], host: Host) -> None:
    """Opens the work's pull request as `kept` says, where the steering names a picked need and
    none is open."""
    title = _picked(steering["ost"])
    if title is None:
        return
    what = "gh has no login to open the pull request"
    checked(host, ["gh", "auth", "status"], work.worktree, Missing, what)
    shown = host(["gh", "pr", "view", branch(work, host), "--json", "url,state"], work.worktree)
    if shown.code != 0 and not shown.err.startswith("no pull requests found"):
        said = (shown.out + shown.err).strip()
        raise CantRun(f"gh can't tell whether the branch has a pull request: {said}")
    held = json.loads(shown.out) if shown.code == 0 else {"state": None}
    if held["state"] != "OPEN":
        _opened(work, steering, title, host)


def _picked(ost: dict[str, Any]) -> str | None:
    """The words of the need that the user picked, or None where none is picked yet."""
    return next(
        (each["opportunity"] for each in ost["opportunities"] if each["id"] == ost["target"]), None
    )


def _opened(work: WorkPlace, steering: dict[str, Any], title: str, host: Host) -> str:
    """Opens the work's pull request as a draft, and gives its URL."""
    body = _body(steering["ost"]["outcome"], steering["state"]["issues"])
    create = ["gh", "pr", "create", "--draft", "--head", branch(work, host), "--title", title]
    made = checked(
        host, [*create, "--body", body], work.worktree, Missing, "gh may not open the pull request"
    )
    return made.out.strip()


def _body(goal: str, issues: dict[str, list[int]]) -> str:
    """The pull request's body: the work's outcome, then a line naming each issue that the work
    closes and each that it refers to."""
    lines = [f"Closes #{each}" for each in issues["closes"]]
    lines += [f"Refs #{each}" for each in issues["refs"]]
    return "\n\n".join([goal, "\n".join(lines)]) if lines else goal


def _commit_all(work: WorkPlace, message: str, host: Host) -> None:
    """Commits each change in the work's worktree with the message, where there's one."""
    _git(host, work, "add", "-A")
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
