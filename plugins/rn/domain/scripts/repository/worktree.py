"""Decides how a run's worktree comes to be and is found again: made with its branch from the
default branch that origin's HEAD names, with the run's folder empty for the pruner's first
result; found from the runs' branches whose committed steering hasn't ended, its worktree made
again where none lies; and removed, here and on GitHub, where the user cancels it."""

from __future__ import annotations

import json
import os
from typing import NamedTuple

from fault import CantRun, Missing, Wrong
from host import Host, checked
from place import RunPlace
from steering.due import due

# The line of info/exclude that keeps the runs' worktrees out of the user's untracked files.
_EXCLUDED = "/.claude/worktrees/"
# The branches of the runs: the local ones, and origin's as the repository last fetched them.
_LOCAL = "refs/heads/rn-*"
_ORIGINS = "refs/remotes/origin/rn-*"
# What a pick-up fetches of origin: the runs' branches, each ref of one that origin no longer
# holds pruned, so that a run deleted on GitHub is never picked up.
_FETCH = ["git", "fetch", "-q", "--prune", "origin", f"+refs/heads/rn-*:{_ORIGINS}"]


def new(run: RunPlace, host: Host) -> RunPlace:
    """Makes a run's worktree and its folder.

    Takes: the run to make, named by `place.named` from the day and the slug of the work, and the
    host.
    Gives: the run, made.
    Changes: adds the branch `rn-<name>` from the head of the default branch that
    `git symbolic-ref refs/remotes/origin/HEAD` names, tracking none, checks it out in the run's
    worktree, makes the run's folder there, empty, and keeps the runs' worktrees out of the user's
    untracked files; the user's own worktree and branch stay as they were.
    Refuses: Missing where the run's repository isn't the top of a git repository, or
    `refs/remotes/origin/HEAD` names no default branch; Wrong where a run of the name already lies
    there; CantRun where git fails, with what it said.
    """
    top = host(["git", "rev-parse", "--show-toplevel"], run.repository)
    if top.code != 0 or os.path.realpath(top.out.strip()) != os.path.realpath(run.repository):
        raise Missing(f"{run.repository} isn't the top of a git repository; run /rn:on at its top")
    if os.path.exists(run.worktree):
        raise Wrong(f"a run {run.name} already lies at {run.worktree}; pick it up with /rn:up")
    default = host(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], run.repository)
    if default.code != 0:
        raise Missing(
            "origin's HEAD names no default branch to start the run from; push the default branch"
            " to origin, and run git remote set-head origin --auto"
        )
    add = ["git", "worktree", "add", "-q", "--no-track", "-b", run.branch, run.worktree]
    what = "git can't make the run's worktree"
    checked(host, [*add, default.out.strip()], run.repository, CantRun, what)
    _exclude(run, host)
    os.makedirs(run.folder)
    return run


def _exclude(run: RunPlace, host: Host) -> None:
    """Keeps the runs' worktrees out of what git shows untracked in the user's own worktree, by
    the repository's info/exclude, which no commit holds, where its line isn't there yet."""
    found = host(["git", "rev-parse", "--git-path", "info/exclude"], run.repository)
    path = os.path.join(run.repository, found.out.strip())
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a+", encoding="utf-8") as file:
        file.seek(0)
        if _EXCLUDED not in file.read().splitlines():
            file.write(f"\n{_EXCLUDED}\n")


class Found(NamedTuple):
    """The runs that a pick-up found, newest first, and, where it couldn't ask GitHub for the runs
    it holds, `the runs on GitHub, as git can't ask origin: <what git said>`, as one line, else
    None."""

    runs: list[RunPlace]
    unchecked: str | None


def found(repository: str, host: Host) -> Found:
    """The runs to pick up, the worktree of each made again where none lies.

    Takes: the top of the user's repository, and the host.
    Gives: the run of the branch that the user's checkout is on alone, in the checkout, where the
    checkout holds that run's steering, as a session started on the branch names its run; else the
    runs that `left` gives once origin's branches of the runs are fetched, each that
    origin no longer holds pruned; where git can't fetch, such as with no network, those of the
    local branches alone, with what it couldn't check.
    Changes: fetches origin's branches `rn-*`, pruning the refs of those that origin no longer
    holds; where a run's worktree is gone, prunes git's record of gone worktrees and adds the
    worktree again, on the local branch `rn-<name>` where it lies, else on a new one from
    origin's, so that a pick-up works in a fresh clone or on another machine.
    Refuses: Wrong as `left` refuses; CantRun where git can't make a worktree, with what it said.
    """
    here = _checked_out(repository, host)
    if here is not None:
        return Found([here], None)
    fetched = host(_FETCH, repository)
    unchecked = None
    if fetched.code != 0:
        said = _line(fetched.out + fetched.err)
        unchecked = f"the runs on GitHub, as git can't ask origin: {said}"
    runs = left(repository, host, origins=unchecked is None)
    for run in runs:
        if not os.path.isdir(run.worktree):
            _made_again(run, host)
    return Found(runs, unchecked)


def _checked_out(repository: str, host: Host) -> RunPlace | None:
    """The run of the branch that the user's checkout is on, where the checkout holds its
    steering, else None."""
    branch = host(["git", "branch", "--show-current"], repository).out.strip()
    if not branch.startswith("rn-"):
        return None
    run = RunPlace(repository, branch[len("rn-") :], checkout=True)
    return run if os.path.isfile(run.steering) else None


def left(repository: str, host: Host, origins: bool = True) -> list[RunPlace]:
    """The runs with work left, from the runs' commits.

    Takes: the top of the user's repository, the host, and whether origin's branches count.
    Gives: the run of each branch among the local branches `rn-*` and, where `origins` says so,
    origin's, as the repository last fetched them, newest first by its last commit, each run once,
    by its newest branch, whose committed steering, `.rn/<name>/steering.json` on the branch,
    has something due other than `ended`, as `steering.due` gives it; none where the folder isn't
    a git repository.
    Changes: nothing.
    Refuses: Wrong where a branch's steering isn't JSON, naming the branch and the path.
    """
    refs = [_LOCAL, _ORIGINS] if origins else [_LOCAL]
    listed = host(
        ["git", "for-each-ref", "--sort=-committerdate", "--format=%(refname)", *refs], repository
    )
    seen: set[str] = set()
    runs = []
    for ref in listed.out.split() if listed.code == 0 else []:
        name = ref.rpartition("/")[2][len("rn-") :]
        if name in seen:
            continue
        seen.add(name)
        if _open(repository, ref, f".rn/{name}/steering.json", host):
            runs.append(RunPlace(repository, name))
    return runs


def _open(repository: str, ref: str, path: str, host: Host) -> bool:
    """Whether the steering that the branch commits has something due other than its end."""
    shown = host(["git", "show", f"{ref}:{path}"], repository)
    if shown.code != 0:
        return False
    try:
        steering = json.loads(shown.out)
    except ValueError as error:
        raise Wrong(f"{ref}:{path}: isn't JSON: {error}") from None
    return due(steering) != ["ended"]


def _made_again(run: RunPlace, host: Host) -> None:
    """Makes the run's worktree again, on its local branch, else on one from origin's."""
    host(["git", "worktree", "prune"], run.repository)
    # git takes a branch that only origin holds as a new local branch from origin's, tracking it.
    add = ["git", "worktree", "add", "-q", run.worktree, run.branch]
    checked(host, add, run.repository, CantRun, "git can't make the run's worktree again")
    _exclude(run, host)


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
    `gh pr view rn-<name>` gives one open, then `origin/rn-<name>`, where `git ls-remote` finds
    origin holding the branch and it deleted it; in `kept`, for each that git or gh couldn't ask
    or remove, such as with no network or no login, `the pull request of rn-<name> on GitHub, as
    gh can't ask GitHub: <what gh said>`, `the pull request <URL> on GitHub, as gh can't close
    it: <what gh said>`, `the branch rn-<name> on GitHub, as git can't ask origin: <what git
    said>`, or `the branch rn-<name> on GitHub, as git can't delete it: <what git said>`, each
    one line. A pull request that gh gives closed or merged, such as an earlier run's of the same
    branch's name, is left as it is.
    Changes: removes the run's worktree, with each change in it that isn't committed, and then its
    local branch `rn-<name>`; then closes the branch's open pull request, before the branch goes,
    as GitHub closes it by itself once its branch is deleted; then deletes origin's branch
    `rn-<name>` and the repository's ref of it, or that ref alone where origin holds no such
    branch, so that no later pick-up meets it; the user's own worktree and branch stay as they
    were.
    Refuses: Wrong where the user's checkout is on the run's branch, as rn never removes the
    user's checkout, saying to switch it to another branch first; CantRun where git fails to
    remove the worktree or the branch here, with what it said, the branch then kept where the
    worktree stays.
    """
    if run.checkout:
        raise Wrong(
            f"your checkout is on the run's branch {run.branch}; switch it to another branch, such"
            " as by git switch main, and cancel the run again"
        )
    top = run.repository
    remove = ["git", "worktree", "remove", "--force", run.worktree]
    checked(host, remove, top, CantRun, "git can't remove the run's worktree")
    checked(host, ["git", "branch", "-D", run.branch], top, CantRun, "git can't delete the branch")
    gone = Gone([], [])
    _pull_request_closed(run, host, gone)
    _branch_deleted(run, host, gone)
    return gone


def _pull_request_closed(run: RunPlace, host: Host, gone: Gone) -> None:
    """Closes the run's branch's open pull request, as `gh pr view` gives it, where there's one;
    gh takes an open one of the branch before any closed or merged one."""
    asked = host(["gh", "pr", "view", run.branch, "--json", "state,url"], run.repository)
    if asked.code != 0 and not asked.err.startswith("no pull requests found"):
        said = _line(asked.out + asked.err)
        gone.kept.append(
            f"the pull request of {run.branch} on GitHub, as gh can't ask GitHub: {said}"
        )
        return
    shown = json.loads(asked.out) if asked.code == 0 else {"state": None}
    if shown["state"] != "OPEN":
        return
    closed = host(["gh", "pr", "close", shown["url"]], run.repository)
    if closed.code == 0:
        gone.removed.append(shown["url"])
    else:
        said = _line(closed.out + closed.err)
        gone.kept.append(f"the pull request {shown['url']} on GitHub, as gh can't close it: {said}")


def _branch_deleted(run: RunPlace, host: Host, gone: Gone) -> None:
    """Deletes origin's branch of the run where `git ls-remote` finds it, and the repository's ref
    of origin's branch where origin holds none."""
    head = f"refs/heads/{run.branch}"
    asked = host(["git", "ls-remote", "--heads", "origin", head], run.repository)
    what = f"the branch {run.branch} on GitHub, as git can't"
    if asked.code != 0:
        gone.kept.append(f"{what} ask origin: {_line(asked.out + asked.err)}")
    elif head in [each.partition("\t")[2] for each in asked.out.splitlines()]:
        deleted = host(["git", "push", "-q", "origin", "--delete", head], run.repository)
        if deleted.code == 0:
            gone.removed.append(f"origin/{run.branch}")
        else:
            gone.kept.append(f"{what} delete it: {_line(deleted.out + deleted.err)}")
    else:
        ref = f"refs/remotes/origin/{run.branch}"
        host(["git", "update-ref", "-d", ref], run.repository)


def _line(said: str) -> str:
    """What git or gh said, as one line."""
    return " ".join(said.split())
