"""Decides how a run's worktree comes to be and is found again: made with its branch from the
default branch that origin's HEAD names, with its design tree, and found from the runs' branches
whose committed design tree holds work left, its worktree made again where none lies."""

from __future__ import annotations

import json
import os

from fault import CantRun, Missing, Wrong
from practice import Practice
from tree import form

from repository.host import Host, checked
from repository.place import RunPlace

# The line of info/exclude that keeps the runs' worktrees out of the user's untracked files.
_EXCLUDED = "/.claude/worktrees/"
# The branches of the runs: the local ones, and origin's as the repository last fetched them.
_REFS = ("refs/heads/rn-*", "refs/remotes/origin/rn-*")


def new(
    run: RunPlace, context: form.Context, goal: str, practice: Practice, host: Host
) -> RunPlace:
    """Makes a run's worktree and its design tree with the goal as put.

    Takes: the run to make, named by `place.named` from the day and the user's words in reply
    to `/rn:on`; the run's context, as `tree.form.context` gives it; the goal as the orchestrator
    puts it; the design tree best practice; and the host.
    Gives: the run, made.
    Changes: adds the branch `rn-<name>` from the head of the default branch that
    `git symbolic-ref refs/remotes/origin/HEAD` names, checks
    it out in the run's worktree, and writes there the design tree that `tree.form.started` gives
    for the context and the goal, uncommitted; the user's own worktree and branch stay as they
    were.
    Refuses: Missing where the run's repository isn't the top of a git repository with a commit, or
    `refs/remotes/origin/HEAD` names no default branch; Wrong where the goal is empty, or a run of
    the name already lies there; CantRun where git fails, with what it said.
    """
    if not goal.strip():
        raise Wrong("the goal is empty; give the goal as one sentence with the user as its subject")
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
    start = default.out.strip()
    checked(
        host,
        ["git", "worktree", "add", "-q", "--no-track", "-b", run.branch, run.worktree, start],
        run.repository,
        CantRun,
        "git can't make the run's worktree",
    )
    _exclude(run, host)
    plan = os.path.relpath(run.tree, run.worktree)
    os.makedirs(run.folder)
    form.write(run.tree, form.started(context, goal, plan, practice))
    return run


def _exclude(run: RunPlace, host: Host) -> None:
    """Keeps the runs' worktrees out of what git shows untracked in the user's own worktree, by
    the repository's info/exclude, which no commit holds, where its line isn't there yet."""
    found = host(["git", "rev-parse", "--git-path", "info/exclude"], run.repository)
    path = os.path.join(run.repository, found.out.strip())
    with open(path, "a+", encoding="utf-8") as file:
        file.seek(0)
        if _EXCLUDED not in file.read().splitlines():
            file.write(f"\n{_EXCLUDED}\n")


def newest(repository: str, host: Host) -> RunPlace | None:
    """The run to pick up, from the runs' commits.

    Takes: the top of the user's repository, and the host.
    Gives: the run of the newest branch by its last commit, among the local branches `rn-*` and
    origin's, as the repository last fetched them, whose committed design tree,
    `.rn/<name>/design-tree.json` on the branch, holds a deliverable that isn't done; a run whose
    newest branch holds no such deliverable, or no design tree, is none to pick up. None where
    there's no such run, or the folder isn't a git repository.
    Changes: nothing.
    Refuses: Wrong where a branch's design tree isn't JSON, naming the branch and the path.
    """
    listed = host(
        ["git", "for-each-ref", "--sort=-committerdate", "--format=%(refname)", *_REFS], repository
    )
    seen: set[str] = set()
    for ref in listed.out.split() if listed.code == 0 else []:
        name = ref.rpartition("/")[2][len("rn-") :]
        if name in seen:
            continue
        seen.add(name)
        path = f".rn/{name}/design-tree.json"
        shown = host(["git", "show", f"{ref}:{path}"], repository)
        if shown.code != 0:
            continue
        try:
            tree = json.loads(shown.out)
        except ValueError as error:
            raise Wrong(f"{ref}:{path}: isn't JSON: {error}") from None
        if any(each["status"] != "done" for each in tree["deliverables"]):
            return RunPlace(repository, name)
    return None


def found(repository: str, host: Host) -> RunPlace | None:
    """The run to pick up, its worktree made again where none lies.

    Takes: the top of the user's repository, and the host.
    Gives: the run that `newest` gives, or None where it gives none.
    Changes: where the run's worktree is gone, prunes git's record of gone worktrees and adds the
    worktree again: on the local branch `rn-<name>` where it lies, else on a new local branch
    `rn-<name>` from origin's, so that a pick-up works in a fresh clone or on another machine;
    keeps the runs' worktrees out of the user's untracked files, as `new` does.
    Refuses: Wrong as `newest` refuses; CantRun where git can't make the worktree, with what it
    said.
    """
    run = newest(repository, host)
    if run is None or os.path.isdir(run.worktree):
        return run
    host(["git", "worktree", "prune"], repository)
    # git takes a branch that only origin holds as a new local branch from origin's, tracking it.
    add = ["git", "worktree", "add", "-q", run.worktree, run.branch]
    checked(host, add, repository, CantRun, "git can't make the run's worktree again")
    _exclude(run, host)
    return run
