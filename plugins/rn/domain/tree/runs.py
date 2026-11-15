"""Decides what makes a run of rn: its name, `<yyyymmdd>-<goal>`, rn's worktree of it in
`.claude/worktrees/rn-<name>/`, its branch, its folder `.rn/<name>/` in that worktree, and which
runs are left to pick up."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

from fault import Wrong
from repository import git

# The prefix of rn's worktree and branch of each run, and where the worktrees lie from the root.
_PREFIX = "rn-"
_WORKTREES = os.path.join(".claude", "worktrees")


@dataclass(frozen=True)
class Run:
    """One run: its name, the folder of rn's worktree of it, its branch, and the run's folder in
    that worktree."""

    name: str
    worktree: str
    branch: str
    folder: str


def start(root: str, goal: str, today: str) -> Run:
    """Makes a run anew.

    Takes: the repository's root, a few words that name the goal, and today's date as `yyyymmdd`.
    Gives: the run.
    Changes: makes the worktree on the run's branch through `repository.git.add_worktree`, and the
    run's folder in it.
    Refuses: fault.Wrong, where the words make no name or a run of that name is left;
    fault.Missing, where the root is no git repository.
    Carries: S1 `O->>T: makes the run's worktree`.
    """
    words = "-".join(re.findall(r"[a-z0-9]+", goal.lower()))
    if not words:
        raise Wrong(f"the words {goal!r} name no goal; give a few words with letters or digits")
    name = f"{today}-{words}"
    if name in (run.name for run in _runs(root)):
        raise Wrong(f"a run named {name} is left; pick it up, or name the goal otherwise")
    run = _run_at(os.path.join(os.path.realpath(root), _WORKTREES, _PREFIX + name), name)
    git.add_worktree(root, run.worktree, run.branch)
    os.makedirs(run.folder)
    return run


def of_folder(folder: str) -> Run | None:
    """The run of the worktree that holds a folder.

    Takes: a folder, such as the one the conversation works in.
    Gives: the run whose worktree holds it, or None where it lies in no run's worktree.
    Changes: nothing.
    Refuses: fault.Missing, where the folder lies in no git repository.
    Carries: S5 `A->>T: gets the run of the worktree that holds the folder`; S1 `A-->>GD: fails, as
    the folder lies in no run's worktree yet`.
    """
    here = os.path.realpath(folder)
    holding = [run for run in _runs(folder) if (here + os.sep).startswith(run.worktree + os.sep)]
    return max(holding, key=lambda run: len(run.worktree), default=None)


def left(folder: str) -> tuple[Run, ...]:
    """The runs left to pick up.

    Takes: any folder of the repository.
    Gives: each run whose worktree is still there, by its name.
    Changes: nothing.
    Refuses: fault.Missing, where the folder lies in no git repository.
    Carries: S5 `A->>T: ... or else the runs left`, and `O->>T: lists the runs left`.
    """
    return tuple(sorted(_runs(folder), key=lambda run: run.name))


def _runs(folder: str) -> list[Run]:
    """Each run whose worktree the repository of the folder holds: a worktree in
    `.claude/worktrees/` of the repository's root, named `rn-<name>` on the branch of that name."""
    found = git.worktrees(folder)
    root = os.path.join(found[0][0], _WORKTREES)
    return [
        _run_at(path, os.path.basename(path)[len(_PREFIX) :])
        for path, branch in found[1:]
        if os.path.dirname(path) == root
        and branch == os.path.basename(path)
        and branch.startswith(_PREFIX)
    ]


def _run_at(worktree: str, name: str) -> Run:
    """The run of the name whose worktree is at the folder."""
    return Run(name, worktree, _PREFIX + name, os.path.join(worktree, ".rn", name))
