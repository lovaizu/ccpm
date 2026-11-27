"""Decides how a run comes to be in the worktree it works in and is found again: made as an empty
folder in a worktree that the orchestrator chose, never the repository's own checkout; found in
each worktree whose branch or uncommitted changes hold its folder; and removed, here and on GitHub,
where the user cancels it."""

from __future__ import annotations

import json
import os
import re
from typing import NamedTuple

from fault import CantRun, Missing, Wrong
from host import Host, checked
from place import RunPlace
from steering.due import due

# The default branch, as origin's HEAD names it, from which each run's branch grows.
_DEFAULT = "refs/remotes/origin/HEAD"
# A run's folder in a path that git gives from a worktree's top.
_RUN = re.compile(r"\.rn/([0-9]{8}-[a-z0-9]+(?:-[a-z0-9]+){0,4})/")


def new(run: RunPlace, host: Host) -> RunPlace:
    """Makes a run's folder in the worktree it works in.

    Takes: the run to make, its worktree the one the orchestrator chose, and its name by
    `place.named` from the day and the slug of the work, and the host.
    Gives: the run, made.
    Changes: makes the run's folder in its worktree, empty, for the pruner's first result.
    Refuses: Missing where the worktree isn't the top of a git worktree; Wrong where it's the
    repository's own checkout, as the user's own work stays as they left it, or where a run of
    the name already lies there.
    """
    top = host(["git", "rev-parse", "--show-toplevel"], run.worktree)
    if top.code != 0 or os.path.realpath(top.out.strip()) != os.path.realpath(run.worktree):
        raise Missing(f"{run.worktree} isn't the top of a git worktree; give the run's worktree")
    if _own_checkout(run.worktree, host):
        raise Wrong(
            f"{run.worktree} is the repository's own checkout; give a worktree for the run, made"
            " by the repository's rules or at the default place"
        )
    if os.path.exists(run.folder):
        raise Wrong(f"a run {run.name} already lies at {run.folder}; pick it up with /rn:up")
    os.makedirs(run.folder)
    return run


def _own_checkout(worktree: str, host: Host) -> bool:
    """Whether the worktree is the repository's own checkout, whose git folder is the common one."""
    asked = ["git", "rev-parse", "--path-format=absolute", "--git-dir", "--git-common-dir"]
    own, common = checked(host, asked, worktree, CantRun, "git can't name its folder").out.split()
    return os.path.realpath(own) == os.path.realpath(common)


def runs(cwd: str, host: Host) -> list[RunPlace]:
    """Each run of the repository that the folder lies in.

    Takes: a folder in the repository, and the host.
    Gives: for each worktree of the repository, newest first by its last commit, each run whose
    folder the worktree's branch changed since the default branch that origin's HEAD names, or
    that the worktree holds uncommitted; none where the folder lies in no git repository.
    Changes: nothing.
    Refuses: nothing.
    """
    listed = host(["git", "worktree", "list", "--porcelain"], cwd)
    if listed.code != 0:
        return []
    found = []
    for worktree in _newest_first(_worktrees(listed.out), host):
        found += [RunPlace(worktree, name) for name in _names(worktree, host)]
    return found


def left(cwd: str, host: Host) -> list[RunPlace]:
    """The runs with work left, as `runs` gives them, each whose steering has something due other
    than its end, or that has no steering yet.

    Refuses: Wrong where a run's steering isn't JSON, naming its path.
    """
    return [each for each in runs(cwd, host) if _open(each)]


def _worktrees(porcelain: str) -> list[str]:
    paths = [
        line[len("worktree ") :] for line in porcelain.splitlines() if line.startswith("worktree ")
    ]
    return [each for each in paths if os.path.isdir(each)]


def _newest_first(worktrees: list[str], host: Host) -> list[str]:
    def when(worktree: str) -> int:
        shown = host(["git", "log", "-1", "--format=%ct"], worktree).out.strip()
        return int(shown or 0)

    return sorted(worktrees, key=when, reverse=True)


def _names(worktree: str, host: Host) -> list[str]:
    """The names of the runs whose folder the worktree's branch changed or holds uncommitted."""
    changed = host(
        ["git", "log", "--format=", "--name-only", f"{_DEFAULT}..HEAD", "--", ".rn"], worktree
    )
    held = host(["git", "status", "--porcelain", "--untracked-files=all", "--", ".rn"], worktree)
    paths = (changed.out if changed.code == 0 else "") + held.out
    names: list[str] = []
    for found in _RUN.finditer(paths):
        if found[1] not in names:
            names.append(found[1])
    return names


def _open(run: RunPlace) -> bool:
    """Whether the run has work left: no steering yet, or one with something due but its end."""
    if not os.path.isfile(run.steering):
        return True
    with open(run.steering, encoding="utf-8") as f:
        try:
            steering = json.load(f)
        except ValueError as error:
            raise Wrong(f"{run.steering}: isn't JSON: {error}") from None
    return due(steering) != ["ended"]


class Gone(NamedTuple):
    """What a cancel did of the run on GitHub: `removed`, each thing that it removed there, and
    `kept`, each thing still there, or that it couldn't ask GitHub of, with why."""

    removed: list[str]
    kept: list[str]


def removed(run: RunPlace, host: Host) -> Gone:
    """Removes a run that the user cancels, here and on GitHub.

    Takes: the run, and the host.
    Gives: what it did of the run on GitHub, as GitHub itself answers, as a ref here may outlive
    the branch it records: in `removed`, the URL of the pull request that it closed, where
    `gh pr view <branch>` gives one open, then `origin/<branch>`, where `git ls-remote` finds
    origin holding the branch and it deleted it; in `kept`, for each that git or gh couldn't ask
    or remove, such as with no network or no login, `the pull request of <branch> on GitHub, as
    gh can't ask GitHub: <what gh said>`, `the pull request <URL> on GitHub, as gh can't close
    it: <what gh said>`, `the branch <branch> on GitHub, as git can't ask origin: <what git
    said>`, or `the branch <branch> on GitHub, as git can't delete it: <what git said>`, each
    one line. A pull request that gh gives closed or merged, such as an earlier run's of the same
    branch's name, is left as it is.
    Changes: removes the run's worktree, with each change in it that isn't committed, and then its
    local branch; then closes the branch's open pull request, before the branch goes, as GitHub
    closes it by itself once its branch is deleted; then deletes origin's branch and the
    repository's ref of it, or that ref alone where origin holds no such branch.
    Refuses: Wrong where the run's worktree is the repository's own checkout, as rn never removes
    it; CantRun where git fails to name the branch, or to remove the worktree or the branch here,
    with what it said, the branch then kept where the worktree stays.
    """
    if _own_checkout(run.worktree, host):
        raise Wrong(f"{run.worktree} is the repository's own checkout, which rn never removes")
    branch = _branch(run, host)
    common = checked(
        host,
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        run.worktree,
        CantRun,
        "git can't name the repository's folder",
    ).out.strip()
    top = os.path.dirname(common)
    remove = ["git", "worktree", "remove", "--force", run.worktree]
    checked(host, remove, top, CantRun, "git can't remove the run's worktree")
    checked(host, ["git", "branch", "-D", branch], top, CantRun, "git can't delete the branch")
    gone = Gone([], [])
    _pull_request_closed(branch, top, host, gone)
    _branch_deleted(branch, top, host, gone)
    return gone


def _branch(run: RunPlace, host: Host) -> str:
    asked = ["git", "branch", "--show-current"]
    return checked(
        host, asked, run.worktree, CantRun, "git can't name the work's branch"
    ).out.strip()


def _pull_request_closed(branch: str, top: str, host: Host, gone: Gone) -> None:
    """Closes the branch's open pull request, as `gh pr view` gives it, where there's one; gh takes
    an open one of the branch before any closed or merged one."""
    asked = host(["gh", "pr", "view", branch, "--json", "state,url"], top)
    if asked.code != 0 and not asked.err.startswith("no pull requests found"):
        said = _line(asked.out + asked.err)
        gone.kept.append(f"the pull request of {branch} on GitHub, as gh can't ask GitHub: {said}")
        return
    shown = json.loads(asked.out) if asked.code == 0 else {"state": None}
    if shown["state"] != "OPEN":
        return
    closed = host(["gh", "pr", "close", shown["url"]], top)
    if closed.code == 0:
        gone.removed.append(shown["url"])
    else:
        said = _line(closed.out + closed.err)
        gone.kept.append(f"the pull request {shown['url']} on GitHub, as gh can't close it: {said}")


def _branch_deleted(branch: str, top: str, host: Host, gone: Gone) -> None:
    """Deletes origin's branch where `git ls-remote` finds it, and the repository's ref of origin's
    branch where origin holds none."""
    head = f"refs/heads/{branch}"
    asked = host(["git", "ls-remote", "--heads", "origin", head], top)
    what = f"the branch {branch} on GitHub, as git can't"
    if asked.code != 0:
        gone.kept.append(f"{what} ask origin: {_line(asked.out + asked.err)}")
    elif head in [each.partition("\t")[2] for each in asked.out.splitlines()]:
        deleted = host(["git", "push", "-q", "origin", "--delete", head], top)
        if deleted.code == 0:
            gone.removed.append(f"origin/{branch}")
        else:
            gone.kept.append(f"{what} delete it: {_line(deleted.out + deleted.err)}")
    else:
        host(["git", "update-ref", "-d", f"refs/remotes/origin/{branch}"], top)


def _line(said: str) -> str:
    """What git or gh said, as one line."""
    return " ".join(said.split())
