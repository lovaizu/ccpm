"""Decides how a run's worktree comes to be and is found again: made with its branch from the
default branch that origin's HEAD names, with its design tree, and found among the worktrees that
hold a run with work left."""

from __future__ import annotations

import os

from fault import CantRun, Missing, Wrong
from practice import Practice
from tree import form

from repository.host import Host, checked
from repository.place import RunPlace

# The line of info/exclude that keeps the runs' worktrees out of the user's untracked files.
_EXCLUDED = "/.claude/worktrees/"


def new(run: RunPlace, goal: str, practice: Practice, host: Host) -> RunPlace:
    """Makes a run's worktree and its design tree with the goal as put.

    Takes: the run to make, named by `place.named` from the day and the user's words after
    `/rn:up`; the goal as the orchestrator puts it; the design tree best practice; and the host.
    Gives: the run, made.
    Changes: adds the branch `rn-<name>` from the head of the default branch that
    `git symbolic-ref refs/remotes/origin/HEAD` names, checks
    it out in the run's worktree, and writes there the design tree that `tree.form.started` gives
    for the goal, uncommitted; the user's own worktree and branch stay as they were.
    Refuses: Missing where the run's repository isn't the top of a git repository with a commit, or
    `refs/remotes/origin/HEAD` names no default branch; Wrong where the goal is empty, or a run of
    the name already lies there; CantRun where git fails, with what it said.
    """
    if not goal.strip():
        raise Wrong("the goal is empty; give the goal as one sentence with the user as its subject")
    top = host(["git", "rev-parse", "--show-toplevel"], run.repository)
    if top.code != 0 or os.path.realpath(top.out.strip()) != os.path.realpath(run.repository):
        raise Missing(f"{run.repository} isn't the top of a git repository; run /rn:up at its top")
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
    form.write(run.tree, form.started(goal, plan, practice))
    return run


def _exclude(run: RunPlace, host: Host) -> None:
    """Keeps the runs' worktrees out of what git shows untracked in the user's own worktree, by
    the repository's info/exclude, which no commit holds."""
    found = host(["git", "rev-parse", "--git-path", "info/exclude"], run.repository)
    with open(os.path.join(run.repository, found.out.strip()), "a", encoding="utf-8") as file:
        file.write(f"\n{_EXCLUDED}\n")


def paused(repository: str) -> list[RunPlace]:
    """The runs that can be picked up.

    Takes: the top of the user's repository.
    Gives: each run under `.claude/worktrees/rn-*/` whose design tree holds a deliverable that
    isn't done, newest first by its name; none where there's no such run.
    Changes: nothing.
    Refuses: Wrong where a run's design tree isn't JSON, naming its path.
    """
    worktrees = os.path.join(repository, ".claude", "worktrees")
    if not os.path.isdir(worktrees):
        return []
    found = []
    for folder in os.listdir(worktrees):
        if not folder.startswith("rn-"):
            continue
        run = RunPlace(repository, folder[len("rn-") :])
        if not os.path.isfile(run.tree):
            continue
        tree = form.read(run.tree)
        if any(each["status"] != "done" for each in tree["deliverables"]):
            found.append(run)
    return sorted(found, key=lambda each: each.name, reverse=True)
