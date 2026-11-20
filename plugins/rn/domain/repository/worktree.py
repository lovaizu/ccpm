"""Decides how a run's worktree comes to be and is found again: made with its branch from the
repository's default branch, with its design tree, and found among the worktrees that hold a run
with work left."""

from __future__ import annotations

from practice import Practice

from repository.host import Host
from repository.place import RunPlace


def new(run: RunPlace, goal: str, practice: Practice, host: Host) -> RunPlace:
    """Makes a run's worktree and its design tree with the goal as put.

    Takes: the run to make, named by `place.named` from the day and the user's words after
    `/rn:up`; the goal as the orchestrator puts it; the design tree best practice; and the host.
    Gives: the run, made.
    Changes: adds the branch `rn-<name>` from the head of the repository's default branch, checks
    it out in the run's worktree, and writes there the design tree that `tree.form.started` gives
    for the goal, uncommitted; the user's own worktree and branch stay as they were.
    Refuses: Missing where the run's repository isn't the top of a git repository with a commit,
    or has no default branch; Wrong where the goal is empty, or a run of the name already lies
    there; CantRun where git fails, with what it said.
    """
    raise NotImplementedError("repository.worktree.new")


def paused(repository: str) -> list[RunPlace]:
    """The runs that can be picked up.

    Takes: the top of the user's repository.
    Gives: each run under `.claude/worktrees/rn-*/` whose design tree holds a deliverable that
    isn't done, newest first by its name; none where there's no such run.
    Changes: nothing.
    Refuses: Wrong where a run's design tree isn't JSON, naming its path.
    """
    raise NotImplementedError("repository.worktree.paused")
