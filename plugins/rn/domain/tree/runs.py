"""Decides what makes a run of rn: its name, `<yyyymmdd>-<goal>`, rn's worktree of it in
`.claude/worktrees/rn-<name>/`, its branch, its folder `.rn/<name>/` in that worktree, and which
runs are left to pick up."""

from __future__ import annotations

from dataclasses import dataclass


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
    raise NotImplementedError("runs.start")


def of_folder(folder: str) -> Run | None:
    """The run of the worktree that holds a folder.

    Takes: a folder, such as the one the conversation works in.
    Gives: the run whose worktree holds it, or None where it lies in no run's worktree.
    Changes: nothing.
    Refuses: fault.Missing, where the folder lies in no git repository.
    Carries: S5 `A->>T: gets the run of the worktree that holds the folder`; S1 `A-->>GD: fails, as
    the folder lies in no run's worktree yet`.
    """
    raise NotImplementedError("runs.of_folder")


def left(folder: str) -> tuple[Run, ...]:
    """The runs left to pick up.

    Takes: any folder of the repository.
    Gives: each run whose worktree is still there, by its name.
    Changes: nothing.
    Refuses: fault.Missing, where the folder lies in no git repository.
    Carries: S5 `A->>T: ... or else the runs left`, and `O->>T: lists the runs left`.
    """
    raise NotImplementedError("runs.left")
