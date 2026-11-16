"""Decides what tree.py commits on the work's branch, when, and with what message, when it pushes,
through repository, and how it reads the design tree's past back from the branch: a decision's
ground, the message of the commit that made it, and the commit at which a deliverable was done."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from typing import Any

from repository import git

from tree.runs import Run


def commit(run: Run, paths: Sequence[str], message: str) -> str:
    """Commits the run's files.

    Takes: the run, each path from the worktree to commit, `.` for all of the worktree, and the
    commit's message: a decision's ground, or the step that ended.
    Gives: the commit's ID, or HEAD's where nothing changed.
    Changes: commits through `repository.git.commit`, with the message word for word, so that the
    user finds a decision's ground in git.
    Refuses: fault.CantRun, where git fails.
    Carries: S1 `K->>T: writes them, and commits them with each decision's ground as the message`,
    `G->>T: commits its work at the end of each step`; S4 `O->>T: commits and pushes each role's
    work so far`.
    """
    return git.commit(run.worktree, paths, message)


def push(run: Run) -> None:
    """Pushes the work's branch.

    Takes: the run.
    Gives: nothing.
    Changes: pushes through `repository.git.push`.
    Refuses: fault.Missing, naming what's missing, where git can't push.
    Carries: S3 `O->>T: pushes the work`, `T->>RP: pushes`, and `T-->>O: what's missing`; S4 the
    same.
    """
    git.push(run.worktree, run.branch)


def ground(run: Run, path: str) -> str:
    """The ground of a node of the design tree.

    Takes: the run, and the node's path, such as
    `deliverables/0/necessary_conditions/0/decisions/0`.
    Gives: the message, word for word, of the latest commit that changed the node as the design tree
    holds it, or "" where no commit did.
    Changes: nothing.
    Refuses: fault.CantRun, where git fails.
    Carries: S1 `A->>T: ... the Cut`, whose decisions each carry their ground, which the design
    tree keeps only in git.
    """
    tree = os.path.relpath(os.path.join(run.folder, "design-tree.json"), run.worktree)
    commits = git.history(run.worktree, tree)
    changed = (
        message
        for (commit_id, message), before in zip(commits, [*commits[1:], None])
        if _node(git.file_at(run.worktree, commit_id, tree), path)
        != (_node(git.file_at(run.worktree, before[0], tree), path) if before else None)
    )
    return next(changed, "")


def done_at(run: Run, deliverable: str) -> str:
    """The commit at which a deliverable was last done.

    Takes: the run, and the deliverable's path, as its `path` in the design tree holds it.
    Gives: the ID of the latest commit that changed the deliverable's status in the design tree to
    `done`, found by the deliverable's path, not its place among the deliverables, which changes
    as the plan does; or "" where no commit did, as for a deliverable never done.
    Changes: nothing.
    Refuses: fault.CantRun, where git fails.
    Carries: S1 `A->>T: gets each deliverable doing, and the Cut of the first that no start that
    runs holds, with the path of a new Record for the start (Cut)`, as the Cut of a deliverable
    done before gives the commit it was done at, which the design tree keeps only in git.
    """
    raise NotImplementedError("branch.done_at")


def _node(text: str, path: str) -> Any:
    """The node at the path in the design tree's text, None where it holds none."""
    node: Any = json.loads(text)
    for part in path.split("/"):
        if isinstance(node, list) and part.isdigit() and int(part) < len(node):
            node = node[int(part)]
        elif isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None
    return node
