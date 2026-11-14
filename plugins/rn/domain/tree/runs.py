"""Decides each run's name, worktree, branch, and folder, and the runs left in the repository with
where each stopped: a run is `<yyyymmdd>-<goal>`, its worktree `.claude/worktrees/rn-<run>/` on the
branch `rn/<run>`, and its folder `.rn/<run>/` in that worktree."""

from __future__ import annotations

import datetime
from dataclasses import dataclass

from tree.rounds import Place

RN = ".rn"
WORKTREES = ".claude/worktrees"


@dataclass(frozen=True)
class Run:
    """One run: its name, the root of the repository, its worktree, its branch, and its folder,
    each path whole."""

    name: str
    root: str
    worktree: str
    branch: str
    folder: str


@dataclass(frozen=True)
class Left:
    """A run left in the repository, with the name of each deliverable doing, each role's Place in
    its last round, and the point or the Sign-off that waits for the user, "" for none."""

    run: Run
    making: tuple[str, ...] = ()
    places: tuple[Place, ...] = ()
    waiting: str = ""


def name(words: str, today: datetime.date) -> str:
    """The run's name from the words the orchestrator gave and the day, such as
    `20261114-type-hints-for-invoicer` for `type hints for invoicer`. Raises Wrong where the words
    hold no letter or digit to name it by."""
    raise NotImplementedError("runs.name")


def title(run: Run) -> str:
    """The run's words, as the user reads them, such as `type hints for invoicer`."""
    raise NotImplementedError("runs.title")


def of(root: str, name: str) -> Run:
    """The run of the name in the repository at the root."""
    raise NotImplementedError("runs.of")


def here(cwd: str) -> Run:
    """The run of the worktree that holds the folder. Raises Wrong where no run's worktree holds
    it."""
    raise NotImplementedError("runs.here")


def left(folder: str) -> tuple[Left, ...]:
    """Each run left in the repository that holds the folder, from its root or from any worktree
    of it, in the order of their names: each worktree of a run that git lists, whose folder the run
    keeps; none where no repository holds the folder."""
    raise NotImplementedError("runs.left")
