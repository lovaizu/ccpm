"""Decides how a run's worktree comes to be and is found again: made with its branch from the
default branch that origin's HEAD names, with the run's folder empty for the pruner's first
result; and found from the runs' branches whose committed steering hasn't ended, its worktree
made again where none lies."""

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
    Gives: the runs that `left` gives once origin's branches of the runs are fetched, each that
    origin no longer holds pruned; where git can't fetch, such as with no network, those of the
    local branches alone, with what it couldn't check.
    Changes: fetches origin's branches `rn-*`, pruning the refs of those that origin no longer
    holds; where a run's worktree is gone, prunes git's record of gone worktrees and adds the
    worktree again, on the local branch `rn-<name>` where it lies, else on a new one from
    origin's, so that a pick-up works in a fresh clone or on another machine.
    Refuses: Wrong as `left` refuses; CantRun where git can't make a worktree, with what it said.
    """
    fetched = host(_FETCH, repository)
    unchecked = None
    if fetched.code != 0:
        said = " ".join((fetched.out + fetched.err).split())
        unchecked = f"the runs on GitHub, as git can't ask origin: {said}"
    runs = left(repository, host, origins=unchecked is None)
    for run in runs:
        if not os.path.isdir(run.worktree):
            _made_again(run, host)
    return Found(runs, unchecked)


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
